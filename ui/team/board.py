import streamlit as st
import pandas as pd
from datetime import datetime
from utils.factory import (
    get_account_repository,
    get_post_repository
)


st.header("📋 게시판")
st.caption("팀 멤버들과 스킬, 팁, 정보를 공유하세요")
#st.write(" ")

#print(st.session_state.get("current_user"))

account_repo = get_account_repository()
post_repo = get_post_repository()

# 현재 사용자 정보 (세션에서 가져오기)
if "current_user" not in st.session_state or st.session_state.current_user is None:
    st.info("로그인이 필요합니다.")
    st.stop()

current_user = st.session_state.current_user
current_user_id = current_user.get("uid")
current_account = account_repo.get_account_by_uid(current_user_id)


# 분류 필터
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    selected_category = st.selectbox("분류", ["전체", "일반", "기술", "팁"], label_visibility="hidden")

st.write(" ")

# 게시물 조회
category_filter = None if selected_category == "전체" else selected_category
posts = post_repo.list_posts(category=category_filter)

if not posts:
    st.info("등록된 게시물이 없습니다.")
    st.write(" ")
else:
    # 게시물 목록 표시
    for post in posts:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])

            with col1:
                # 공지 표시
                if post.get("isPinned"):
                    st.write(f"📣 **[공지]** {post["title"]} ( {post.get("comment_count", 0)} )")
                else:
                    category_emoji = {
                        "일반": "🔔",
                        "기술": "📝",
                        "팁": "💡"                        
                    }.get(post.get("category", "일반"), "📝")
                    st.write(f"{category_emoji} {post['title']} ( {post.get("comment_count", 0)} )")

                # 작성자 정보
                st.caption(f"작성자: {post.get('author_name', 'Unknown')} / 작성일 : {post.get('created_at', 'N/A')}")            

            # 게시물 상세보기 / 댓글
            if st.button("본문", key=f"view_{post['id']}", width="stretch"):
                if st.session_state.get("selected_post_id") == post["id"] or st.session_state.get("edit_post_id") == post["id"]:
                    # 이미 열려있는 경우 닫기 (본문 상세 또는 수정 상태)
                    if "selected_post_id" in st.session_state:
                        del st.session_state.selected_post_id
                    if "edit_post_id" in st.session_state:
                        del st.session_state.edit_post_id
                else:
                    # 새로 열기
                    st.session_state.selected_post_id = post["id"]
                st.rerun()

            if st.session_state.get("selected_post_id") == post["id"]:
                post_id = post["id"]
                post_detail = post_repo.get_post(post_id)

                if post_detail:
                    st.divider()
                    st.subheader(post_detail["title"])
                    st.caption(f"작성자: {post.get('author_name', 'Unknown')} / 작성일 : {post.get('created_at', 'N/A')}")

                    st.divider()
                    st.write(post_detail["content"])
                    st.divider()

                    if post_detail.get("author_id") == current_user_id or current_account.get("role") == "admin":
                        col1, col2, col3 = st.columns([1, 14, 1])
                        with col1:
                            if st.button("수정", key=f"edit_content_{post_id}"):
                                st.session_state.edit_post_id = post_id
                                if "selected_post_id" in st.session_state:
                                    del st.session_state.selected_post_id
                                st.rerun()
                        with col3:
                            if st.button("삭제", key=f"delete_{post_id}", type="primary"):
                                try:
                                    post_repo.delete_post(post_id)
                                    st.session_state.success_message = "게시물이 삭제되었습니다!"
                                    if "selected_post_id" in st.session_state:
                                        del st.session_state.selected_post_id
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"삭제 실패: {e}")
                        st.write(" ")

                    st.subheader(f"💬 댓글 ({len(post_repo.list_comments(post_id))})")                   

                    comments = post_repo.list_comments(post_id)
                    for comment in comments:
                        with st.container(border=True, horizontal_alignment="right"):
                            col1, col2 = st.columns([15, 0.5])
                            with col1:
                                st.write(f"**{comment.get('author_name', 'Unknown')}** ({comment.get('created_at', 'N/A')})")
                                st.write(comment["content"])
                            with col2:
                                if comment.get("author_id") == current_user_id:
                                    if st.button(
                                            icon="❌",
                                            label="",
                                            key=f"delete_comment_{comment['id']}",
                                            type="tertiary",
                                            width="stretch"                                            
                                        ):
                                        try:
                                            post_repo.delete_comment(post_id, comment["id"])
                                            st.session_state.success_message = "댓글이 삭제되었습니다!"
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"삭제 실패: {e}")

                    with st.expander("댓글 작성", expanded=True):
                        with st.form(f"comment_form_{post_id}"):
                            comment_content = st.text_area("댓글", height=80)
                            if st.form_submit_button("등록", type="primary"):
                                if comment_content:
                                    try:
                                        post_repo.add_comment(post_id, {
                                            "author_id": current_user_id,
                                            "content": comment_content
                                        })
                                        st.session_state.success_message = "댓글이 등록되었습니다!"
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"댓글 등록 실패: {e}")
                                else:
                                    st.error("댓글 내용을 입력해주세요.")

                    st.divider()

            if st.session_state.get("edit_post_id") == post["id"]:
                post_id = post["id"]
                post_detail = post_repo.get_post(post_id)

                if post_detail:
                    st.divider()
                    st.subheader("게시물 수정")
                    with st.form(f"edit_post_form_{post_id}"):
                        edit_category = st.selectbox("분류", ["일반", "기술", "팁"], 
                                                        index=["일반", "기술", "팁"].index(post_detail.get("category", "일반")))
                        edit_title = st.text_input("제목", value=post_detail["title"])
                        edit_content = st.text_area("내용", value=post_detail["content"], height=200)
                        
                        
                        st.write(" ") # 빈 줄 추가

                        if st.form_submit_button("수정", type="primary"):
                            if edit_title and edit_content:
                                try:
                                    post_repo.update_post(post_id, {
                                        "title": edit_title,
                                        "content": edit_content,
                                        "category": edit_category
                                    })
                                    st.session_state.success_message = "게시물이 수정되었습니다!"
                                    if "edit_post_id" in st.session_state:
                                        del st.session_state.edit_post_id
                                    st.session_state.selected_post_id = post_id
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"수정 실패: {e}")

                        st.write(" ") # 빈 줄 추가

                    st.write(" ") # 빈 줄 추가                 


    st.divider()


st.write(" ") # 빈 줄 추가

# 게시물 작성 폼
with st.expander("✍️ 글쓰기", expanded=True):
    with st.form("post_form"):
        
        # 공지 고정 체크박스 (관리자만 표시)
        if current_account.get("role") == "admin":
            post_pinned = st.checkbox("공지", value=False)
        else:
            post_pinned = False  # 일반 사용자는 공지 고정 불가
        st.write(" ") # 빈 줄 추가

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
                post_category = st.selectbox("분류", ["일반", "기술", "팁"])

        post_title = st.text_input("제목", placeholder="스킬이나 팁을 공유해주세요")
        post_content = st.text_area("내용", height=200, placeholder="자세한 내용을 입력하세요")               

        st.write(" ") # 빈 줄 추가

        if st.form_submit_button("작성", type="primary"):
            if post_title and post_content:
                try:
                    # 게시물 생성 및 ID 반환
                    post_id = post_repo.create_post({
                        "title": post_title,
                        "content": post_content,
                        "author_id": current_user_id,
                        "category": post_category
                    })
                    # 공지 고정 (관리자만 가능)
                    if post_pinned and current_account.get("role") == "admin":
                        post_repo.pin_post(post_id, True)

                    st.session_state.success_message = "게시물이 등록되었습니다!"
                    st.rerun()
                except Exception as e:
                    st.error(f"게시물 등록 실패: {e}")
            else:
                st.error("제목과 내용을 입력해주세요.")

        st.write(" ") # 빈 줄 추가

    

    # 성공/에러 메시지 표시
    if "success_message" in st.session_state:
        st.success(st.session_state.success_message)
        del st.session_state.success_message
    if "error_message" in st.session_state:
        st.error(st.session_state.error_message)
        del st.session_state.error_message

    st.divider()

    
