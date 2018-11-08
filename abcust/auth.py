from flask_dance.contrib.slack import slack


def authorized():
    # TODO: slack에 수시로 토큰 유효 테스트
    return slack.authorized
