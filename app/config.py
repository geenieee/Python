"""
애플리케이션 설정
"""
import os


# 세션 설정
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-12345")
SESSION_MAX_AGE = 3600  # 1시간
SESSION_COOKIE_NAME = "ldap_session"
SESSION_SAME_SITE = "lax"
SESSION_HTTPS_ONLY = False  # 개발 환경에서는 False (운영에서는 True 권장)

# LDAP 조회 속성 목록
LDAP_USER_ATTRIBUTES = [
    'cn', 'displayName', 'sAMAccountName', 'userPrincipalName',
    'mail', 'telephoneNumber', 'mobile', 'department', 'title',
    'company', 'manager', 'memberOf', 'whenCreated', 'whenChanged',
    'lastLogon', 'pwdLastSet', 'userAccountControl', 'distinguishedName',
    'description', 'physicalDeliveryOfficeName', 'streetAddress',
    'l', 'st', 'postalCode', 'co', 'employeeID', 'employeeNumber'
]

# LDAP 속성 한글 레이블
LDAP_ATTR_LABELS = {
    'cn': '이름 (CN)',
    'displayName': '표시 이름',
    'sAMAccountName': '로그인 ID',
    'userPrincipalName': 'UPN',
    'mail': '이메일',
    'telephoneNumber': '전화번호',
    'mobile': '휴대폰',
    'department': '부서',
    'title': '직책',
    'company': '회사',
    'manager': '관리자',
    'memberOf': '소속 그룹',
    'whenCreated': '생성일',
    'whenChanged': '수정일',
    'lastLogon': '마지막 로그인',
    'pwdLastSet': '비밀번호 변경일',
    'userAccountControl': '계정 상태',
    'distinguishedName': 'DN',
    'description': '설명',
    'physicalDeliveryOfficeName': '사무실',
    'streetAddress': '주소',
    'l': '도시',
    'st': '시/도',
    'postalCode': '우편번호',
    'co': '국가',
    'employeeID': '사번',
    'employeeNumber': '직원번호'
}
