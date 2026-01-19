"""
LDAP/AD 관련 서비스 로직
"""
import datetime
from typing import Optional, Dict, Any
from ldap3 import Server, Connection, ALL, SUBTREE, MODIFY_REPLACE

from app.config import LDAP_USER_ATTRIBUTES, LDAP_ATTR_LABELS


def test_ldap_connection(server: str, bind_user: str, bind_password: str) -> tuple[bool, str]:
    """LDAP 연결 테스트"""
    try:
        ldap_server = Server(server, get_info=ALL, connect_timeout=10)
        conn = Connection(ldap_server, user=bind_user, password=bind_password, auto_bind=True)
        conn.unbind()
        return True, "연결 성공"
    except Exception as e:
        return False, str(e)


def search_user(ldap_config: Dict[str, str], username: str) -> Dict[str, Any]:
    """AD 사용자 검색"""
    try:
        ldap_server = Server(ldap_config["server"], get_info=ALL)
        conn = Connection(
            ldap_server,
            user=ldap_config["bind_user"],
            password=ldap_config["bind_password"],
            auto_bind=True
        )
        
        search_filter = f"(sAMAccountName={username})"
        conn.search(
            search_base=ldap_config["base_dn"],
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=LDAP_USER_ATTRIBUTES
        )
        
        if len(conn.entries) == 0:
            conn.unbind()
            return {"success": False, "message": f"'{username}' 계정을 찾을 수 없습니다."}
        
        entry = conn.entries[0]
        
        # 속성을 딕셔너리로 변환
        attributes = {}
        for attr_name, label in LDAP_ATTR_LABELS.items():
            try:
                value = getattr(entry, attr_name, None)
                if value is not None:
                    val = value.value if hasattr(value, 'value') else str(value)
                    if val:
                        # memberOf 처리 (CN만 추출)
                        if attr_name == 'memberOf' and isinstance(val, list):
                            val = [v.split(',')[0].replace('CN=', '') for v in val[:5]]
                            if len(entry.memberOf.values) > 5:
                                val.append(f'... 외 {len(entry.memberOf.values) - 5}개')
                        attributes[label] = val
            except Exception:
                pass
        
        conn.unbind()
        
        return {
            "success": True,
            "username": username,
            "attributes": attributes
        }
        
    except Exception as e:
        return {"success": False, "message": f"LDAP 연결 오류: {str(e)}"}


def check_lock_status(ldap_config: Dict[str, str], username: str) -> Dict[str, Any]:
    """계정 잠금 상태 확인"""
    try:
        ldap_server = Server(ldap_config["server"], get_info=ALL)
        conn = Connection(
            ldap_server,
            user=ldap_config["bind_user"],
            password=ldap_config["bind_password"],
            auto_bind=True
        )
        
        search_filter = f"(sAMAccountName={username})"
        conn.search(
            search_base=ldap_config["base_dn"],
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=[
                'distinguishedName', 'sAMAccountName', 'displayName',
                'mail', 'department', 'lockoutTime', 'userAccountControl',
                'msDS-User-Account-Control-Computed',
                'badPwdCount'
            ]
        )
        
        if len(conn.entries) == 0:
            conn.unbind()
            return {"success": False, "message": f"'{username}' 계정을 찾을 수 없습니다."}
        
        entry = conn.entries[0]
        
        # 잠금 상태 확인
        lockout_time = None
        is_locked = False
        
        # 방법 1: msDS-User-Account-Control-Computed 속성 확인 (가장 정확)
        try:
            uac_computed = getattr(entry, 'msDS-User-Account-Control-Computed', None)
            if uac_computed and uac_computed.value:
                is_locked = bool(int(uac_computed.value) & 0x0010)
        except Exception:
            pass
        
        # 방법 2: lockoutTime 속성으로 확인 (백업)
        try:
            lockout_value = entry.lockoutTime.value
            if lockout_value is not None:
                if isinstance(lockout_value, datetime.datetime):
                    if lockout_value.year > 1601:
                        is_locked = True
                        lockout_time = lockout_value.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(lockout_value, int) and lockout_value > 0:
                    is_locked = True
                    windows_epoch = datetime.datetime(1601, 1, 1)
                    lockout_datetime = windows_epoch + datetime.timedelta(microseconds=lockout_value // 10)
                    lockout_time = lockout_datetime.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
        
        # 사용자 정보 추출
        user_dn = _get_attr_value(entry, 'distinguishedName')
        display_name = _get_attr_value(entry, 'displayName')
        email = _get_attr_value(entry, 'mail')
        department = _get_attr_value(entry, 'department')
        
        # 잘못된 비밀번호 시도 횟수
        bad_pwd_count = 0
        try:
            bad_pwd_value = entry.badPwdCount.value
            if bad_pwd_value is not None:
                bad_pwd_count = int(bad_pwd_value)
        except Exception:
            pass
        
        conn.unbind()
        
        return {
            "success": True,
            "username": username,
            "user_dn": user_dn,
            "display_name": display_name,
            "email": email,
            "department": department,
            "is_locked": is_locked,
            "lockout_time": lockout_time,
            "bad_pwd_count": bad_pwd_count
        }
        
    except Exception as e:
        return {"success": False, "message": f"LDAP 연결 오류: {str(e)}"}


def unlock_user_account(ldap_config: Dict[str, str], user_dn: str, username: str) -> Dict[str, Any]:
    """계정 잠금 해제"""
    try:
        ldap_server = Server(ldap_config["server"], get_info=ALL)
        conn = Connection(
            ldap_server,
            user=ldap_config["bind_user"],
            password=ldap_config["bind_password"],
            auto_bind=True
        )
        
        # lockoutTime을 0으로 설정하여 잠금 해제
        result = conn.modify(
            user_dn,
            {'lockoutTime': [(MODIFY_REPLACE, [0])]}
        )
        
        if result:
            conn.unbind()
            return {
                "success": True,
                "message": f"'{username}' 계정의 잠금이 해제되었습니다."
            }
        else:
            error_msg = conn.result.get('description', '알 수 없는 오류')
            conn.unbind()
            return {
                "success": False,
                "message": f"잠금 해제 실패: {error_msg}"
            }
        
    except Exception as e:
        return {"success": False, "message": f"LDAP 연결 오류: {str(e)}"}


def _get_attr_value(entry, attr_name: str) -> Optional[str]:
    """엔트리에서 속성 값 안전하게 추출"""
    try:
        attr = getattr(entry, attr_name, None)
        if attr:
            return attr.value
    except Exception:
        pass
    return None
