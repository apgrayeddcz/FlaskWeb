import requests

if __name__ == '__main__':
  answer = requests.post(
    'https://server-ql6o-main-7ykqoolpza-wm.a.run.app',
    json = {
      # 'key': "srizametov@vk.com",
      'key': 'd60cb9d2-b0d1-40b3-8e64-c0715eda0326',
      # 'key': '1',
      'action': 'cancel_order',
      'order': '978738fb-0d6a-41e7-a460-e10eb070585a', #### выбранное поставщиком задание
      # 'task': '5cb4a2b3-382b-42f3-bbff-58d0d691db06', #### выбранное ботом задание
      # 'status': 'done',
      # 'social': 'vk',
      # 'type_task': 'like',
      # 'count_task': 60,
      # 'link': 'https://m.vk.com/wall-69467117_278'
    },
    verify = False
  )
  answer.encoding = 'utf-8'
  print(answer)