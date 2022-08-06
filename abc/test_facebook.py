from abcust.tasks import facebook

facebook.on_entry.delay({
    'url': 'https://www.byb.kr',
    'name': '테스트',
    'content': '페이스북 새 글 알림을 위한 테스트입니다.'
})
