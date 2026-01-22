"""
Google Workspace 사용자 관리 서비스
"""
from google.oauth2 import service_account
from googleapiclient.discovery import build
from typing import List, Dict, Optional

# 설정
CREDENTIALS_FILE = "credentials.json"
ADMIN_EMAIL = "seongjin.ko@vroong.com"
SCOPES = ["https://www.googleapis.com/auth/admin.directory.user.readonly"]


def get_directory_service():
    """Google Admin Directory API 서비스 객체 생성"""
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=SCOPES
    )
    # 도메인 전체 위임을 위해 관리자 계정으로 위임
    delegated_credentials = credentials.with_subject(ADMIN_EMAIL)
    
    service = build("admin", "directory_v1", credentials=delegated_credentials)
    return service


def get_all_users(max_results: int = 100) -> List[Dict]:
    """
    Google Workspace 사용자 목록 조회
    
    Returns:
        사용자 정보 리스트 (성, 이름, 이메일, 2단계 인증 여부)
    """
    service = get_directory_service()
    
    users_list = []
    page_token = None
    
    while True:
        # 사용자 목록 조회
        results = service.users().list(
            customer="my_customer",  # 현재 도메인의 모든 사용자
            maxResults=max_results,
            pageToken=page_token,
            orderBy="email",
            projection="full"  # 2단계 인증 정보를 위해 full projection 필요
        ).execute()
        
        users = results.get("users", [])
        
        for user in users:
            name = user.get("name", {})
            users_list.append({
                "familyName": name.get("familyName", ""),  # 성
                "givenName": name.get("givenName", ""),    # 이름
                "email": user.get("primaryEmail", ""),      # 이메일
                "isEnrolledIn2Sv": user.get("isEnrolledIn2Sv", False),  # 2단계 인증 등록 여부
                "isEnforcedIn2Sv": user.get("isEnforcedIn2Sv", False),  # 2단계 인증 강제 여부
                "suspended": user.get("suspended", False),  # 계정 정지 여부
                "orgUnitPath": user.get("orgUnitPath", ""),  # 조직 단위
            })
        
        page_token = results.get("nextPageToken")
        if not page_token:
            break
    
    return users_list


def get_user_by_email(email: str) -> Optional[Dict]:
    """
    특정 사용자 정보 조회
    
    Args:
        email: 사용자 이메일
        
    Returns:
        사용자 정보 딕셔너리
    """
    service = get_directory_service()
    
    try:
        user = service.users().get(
            userKey=email,
            projection="full"
        ).execute()
        
        name = user.get("name", {})
        return {
            "familyName": name.get("familyName", ""),
            "givenName": name.get("givenName", ""),
            "email": user.get("primaryEmail", ""),
            "isEnrolledIn2Sv": user.get("isEnrolledIn2Sv", False),
            "isEnforcedIn2Sv": user.get("isEnforcedIn2Sv", False),
            "suspended": user.get("suspended", False),
            "orgUnitPath": user.get("orgUnitPath", ""),
            "creationTime": user.get("creationTime", ""),
            "lastLoginTime": user.get("lastLoginTime", ""),
        }
    except Exception as e:
        print(f"Error fetching user {email}: {e}")
        return None
