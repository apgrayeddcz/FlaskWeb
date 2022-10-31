import flask
import flask_restful
import uuid
import os
import sys
import time
import json
import datetime
import random

filename = str(os.path.basename(sys.argv[0]))
filelink = str(__file__)[:-(len(filename))].replace('/ap','')
filelink = 'templates/'
def get_key_by_value(dict_, value):
  return list(dict_.keys())[list(dict_.values()).index(value)]
def is_number(string, type_number):
  if type_number == 'float':
    try:
      float(string)
      return True
    except:
      return False
  elif type_number == 'int':
    try:
      int(string)
      return True
    except:
      return False
def load_json(link):
  # while True:
  #   try:
      return json.load(
        open(link, 'r', encoding='utf-8')
      )
    # except:
    #   pass
def save_json(data, link):
  # while True:
  #   try:
      json.dump(
        data,
        open(link, 'w', encoding='utf-8')
      )
      # break
    # except:
    #   pass

pause_between_orders = [10, 60]
platforms = {
  'SmmLaba': "d60cb9d2-b0d1-40b3-8e64-c0715eda0326",
  'test': '1',
  'MAIN': 'd93a712c-0643-420c-b575-01af693d6cfc',
}
bots = load_json(f"{filelink}/bots_list.json")
print(bots)
socials = {
  'vk': {
    'type_tasks': [
      'like',
      'post',
      'viewPost',
      'viewVideo',
      ],
    'max': 200,
  },
  'ok': {
    'type_tasks': [
      'like',
      'post',
      ],
    'max': 200
  },
  'dzen': {

  }
}

#Проверить работу сервера
def check(json_data):
  return {'status': True}, 200

#перевести order в order для отправки
def order_to_answer(order):
  to_del_info = [
    'last_action',
    'pause',
    'bots_done',
    'bots_in_work',
    'platform',
    'errors',
  ]
  for info in to_del_info:
    del order[info]

  return order
#получить переменные для запросов
def get_social_info(json_data):
  return {'status': True, 'result': socials}, 200
#создать заказ
def create_order(json_data):
  # key ключ заказчика
  # social социалка для создания заказа
  # type_task тип задания для создания заказа
  # count_task количество выполнений
  # ссылка на выполнение

  key = json_data['key']
  social = False
  type_task = False
  count_task = False
  link = False

  if 'social' not in json_data:
    return {'status': 'error', 'message': 'social not found'}, 404
  elif json_data['social'] not in socials:
    return {'status': 'error', 'message': 'social incorrect'}, 404
  social = json_data['social']

  if 'type_task' not in json_data:
    return {'status': 'error', 'message': 'type_task not found'}, 404
  elif json_data['type_task'] not in socials[social]['type_tasks']:
    return {'status': 'error', 'message': 'type_task incorrect'}, 404
  type_task = json_data['type_task']

  if 'link' not in json_data:
    return {'status': 'error', 'message': 'link not found'}, 404
  link = json_data['link']

  if 'count_task' not in json_data:
    return {'status': 'error', 'message': 'count_task not found'}, 404
  elif is_number(json_data['count_task'], 'int') == False:
    return {'status': 'error', 'message': 'count_task must be a number'}, 404
  elif int(json_data['count_task']) > socials[social]['max']:
    return {'status': 'error', 'message': f"count_task should not be more than {socials[social]['max']}"}, 404
  count_task = int(json_data['count_task'])

  new_order = {
    'id': str(uuid.uuid4()),
    'platform': get_key_by_value(platforms, json_data['key']),
    'social': social,
    'type_task': type_task,
    'link': link,
    'status': 'in_queue',
    'status_count': {
      'completed': 0,
      'ordered': count_task,
      'total': count_task,
    },
    'last_action': False,
    'pause': False,
    'bots_done': [],
    'bots_in_work': [],
    'errors': [], 
  }
  links_tasks_info = load_json(f"{filelink}/links_tasks_info.json")
  if link not in links_tasks_info:
    links_tasks_info[link] = {}
    links_tasks_info[link][type_task] = []
  else:
    if new_order['type_task'] not in links_tasks_info[link]:
      links_tasks_info[link][type_task] = []
    else:
      bots_done = links_tasks_info[link][type_task]
      max_to_work = len(bots_done)
      if socials[social]['max'] < count_task + len(bots_done):
        return {'status': 'error', 'message': f"The task was in the past, it used to take {len(bots_done)} to complete it, now the maximum number of executions is equal to {social[social]['max'] - len(bots_done)}"}, 404
      new_order['bots_done'] = bots_done
      new_order['status_count']['completed'] += len(bots_done)
      new_order['status_count']['total'] += len(bots_done)
  save_json(links_tasks_info,f"{filelink}/links_tasks_info.json")
  
  active_tasks = load_json(f"{filelink}/active_tasks.json")
  active_tasks[new_order['id']] = new_order
  save_json(active_tasks,f"{filelink}/active_tasks.json")

  return {'status': True, 'result': order_to_answer(new_order)}, 200
#отменить заказ
def cancel_order(json_data):
  # key ключ заказчика
  # order номер заказа

  key = json_data['key']
  if 'order' not in json_data:
    return {'status': 'error', 'message': 'order not found'}, 404

  active_tasks = load_json(f"{filelink}/active_tasks.json")
  if json_data['order'] not in active_tasks:
    return {'status': 'error', 'message': 'order not in active orders'}, 404
  if get_key_by_value(platforms, key) != active_tasks[json_data['order']]['platform'] or get_key_by_value(platforms, key) == 'MAIN':
    return {'status': 'error', 'message': 'order incorrect'}, 404

  if get_key_by_value(platforms, key) != active_tasks[json_data['order']]['platform']:
    return {'status': 'error', 'message': 'order incorrect'}, 404
  order = active_tasks[json_data['order']]

  order['status'] = 'cancelled'
  active_tasks[json_data['order']] = order
  save_json(active_tasks, f"{filelink}/active_tasks.json")

  return {'status': True, 'result': order_to_answer(order)}, 200
#Получить статус заказа
def check_order(json_data):
  # key ключ заказчика
  # order номер заказа

  key = json_data['key']
  
  if 'order' not in json_data:
    return {'status': 'error', 'message': 'order not found'}, 404

  history_orders = load_json(f"{filelink}/history_tasks.json")
  active_tasks = load_json(f"{filelink}/active_tasks.json")
  if (
    json_data['order'] not in history_orders and
    json_data['order'] not in active_tasks
    ):
    return {'status': 'error', 'message': 'order incorrect'}, 404
  
  order = False
  if json_data['order'] in active_tasks:
    order = active_tasks[json_data['order']]
  else:
    order = history_orders[json_data['order']]
  if get_key_by_value(platforms, json_data['key']) != order['platform']:
    return {'status': 'error', 'message': 'order incorrect'}, 404

  return {'status': True, 'result': order_to_answer(order)}, 200
#Получить активные заказы
def check_orders(json_data):
  # key ключ заказчика
  # status_order ('all', old, active) статус заказа
  # socials ('all' ['vk', 'ok', 'dzen']) отбор по социальным сетям
  # type_tasks ('all' ['like', 'post', 'comment'...]) отбор по типу услуги

  platform = get_key_by_value(platforms, json_data['key'])
  active_tasks = {}
  history_orders = {}
  socials_filtr = []
  type_tasks_filtr = []

  if 'status_order' not in json_data:
    json_data['status_order'] = 'all'
  if json_data['status_order'] == 'all':
    active_tasks = load_json(f"{filelink}/active_tasks.json")
    history_orders = load_json(f"{filelink}/history_tasks.json")
  elif json_data['status_order'] == 'active':
    active_tasks = load_json(f"{filelink}/active_tasks.json")
  elif json_data['status_order'] == 'old':
    history_orders = load_json(f"{filelink}/history_tasks.json")
  else:
    return {'status': 'error', 'message': 'status_order incorrect'}, 404

  if 'socials' not in json_data:
    json_data['socials'] = 'all'
  if json_data['socials'] == 'all':
    socials_filtr = list(socials.keys())
  elif isinstance(json_data['socials'], list):
    for check_social in json_data['socials']:
      if check_social not in socials:
        return {'status': 'error', 'message': f'{check_social} incorrect'}, 404
    socials_filtr = json_data['socials']
  else:
    return {'status': 'error', 'message': 'socials incorrect'}, 404

  if 'type_tasks' not in json_data:
    json_data['type_tasks'] = 'all'
  if json_data['type_tasks'] == 'all':
    for social in socials_filtr:
      type_tasks_filtr += socials[social]['type_tasks']
      type_tasks_filtr = list(set(type_tasks_filtr))
  elif isinstance(json_data['type_tasks'], list):
    for social in socials_filtr:
      for check_type_task in json_data['type_tasks']:
        if check_type_task not in socials_filtr[social]['type_tasks']:
          return {'status': 'error', 'message': f'{check_type_task} incorrect'}, 404
        type_tasks_filtr += [check_type_task]
    type_tasks_filtr = list(set(type_tasks_filtr))
  else:
    return {'status': 'error', 'message': 'type_tasks incorrect'}, 404

  data = active_tasks | history_orders
  result = []
  for id_task in data:
    task_info = data[id_task]
    if (
      task_info['platform'] == platform and
      task_info['social'] in socials_filtr and
      task_info['type_task'] in type_tasks_filtr
    ):
      result += [order_to_answer(task_info)]
  return {'status': True, 'result': result}, 200


#Получить список заданий
def get_task(json_data):
  # key ключ бота

  if json_data['key'] not in bots:
    return {'status': 'error', 'message': 'action incorrect'}, 404

  bot = bots[json_data['key']]
  result = []
  tasks = load_json(f"{filelink}/active_tasks.json")

  for task in tasks:
    task_info = tasks[task]
    #Если он уже его выполнял/выполняет
    if (
      bot in task_info['bots_done'] or
      bot in task_info['bots_in_work']
      ):
      continue
    #Если больше 5 ботов выслало ошибку
    if len(task_info['errors']) > 5:
      continue
    #Если задание закончено/отмененно
    if (
        task_info['status'] == 'cancelled' or
        task_info['status'] == 'done'
      ):
      continue
    #Если паралелльно это задание делает более 3 ботов/активные боты на задание делают его лимит
    if (
      len(task_info['bots_in_work']) > 3 or
      len(task_info['bots_in_work']) + task_info['status_count']['completed'] == task_info['status_count']['total']
      ):
      continue
    #Если задержка между заданиями еще не прошла
    if task_info['last_action']:
      date = datetime.datetime.strptime(task_info['last_action'], '%d.%m.%Y %H:%M:%S')
      pause = task_info['pause']
      if (datetime.datetime.now() - date).total_seconds() - pause < 0:
        continue 
    
    result += [task_info]
  
  return {'status': True, 'result': result}, 200 
#Сообщить о старте задания
def send_start_task(json_data):
  # key ключ бота
  # task id задания

  if json_data['key'] not in bots:
    return {'status': 'error', 'message': 'action incorrect'}, 404

  bot = bots[json_data['key']]
  active_tasks = load_json(f"{filelink}/active_tasks.json")
  active_tasks[json_data['task']]['bots_in_work'] += [bot]
  save_json(active_tasks, f"{filelink}/active_tasks.json")

  return {'status': True}, 200 
#Сообщить о статусе выполненого задания
def send_complete_info(json_data):
  # key ключ бота
  # task id задания
  # status {done, done_before, fail}

  if json_data['key'] not in bots:
    return {'status': 'error', 'message': 'action incorrect'}, 404

  bot = bots[json_data['key']]
  active_tasks = load_json(f"{filelink}/active_tasks.json")

  if json_data['status'] == 'done' or json_data['status'] == 'done_before':
    links_tasks_info = load_json(f"{filelink}/links_tasks_info.json")
    task = active_tasks[json_data['task']]
    active_tasks[json_data['task']]['bots_done'] += [bot]
    active_tasks[json_data['task']]['bots_in_work'].remove(bot)
    links_tasks_info[task['link']][task['type_task']] += [bot]
    active_tasks[json_data['task']]['status_count']['completed'] += 1
    active_tasks[json_data['task']]['last_action'] = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    active_tasks[json_data['task']]['pause'] = random.randint(pause_between_orders[0], pause_between_orders[1])
    if active_tasks[json_data['task']]['status_count']['total'] == active_tasks[json_data['task']]['status_count']['completed']:
      active_tasks[json_data['task']]['status'] = 'done'
    elif active_tasks[json_data['task']]['status'] == 'in_queue':
      active_tasks[json_data['task']]['status'] = 'in_work'
  elif json_data['status'] == 'fail':
    active_tasks[json_data['task']]['errors'] += [bot]
    active_tasks[json_data['task']]['bots_in_work'].remove(bot)
  
  save_json(active_tasks,f"{filelink}/active_tasks.json")
  save_json(links_tasks_info,f"{filelink}/links_tasks_info.json")

  return {'status': True}, 200 


#Перевести заказ в history(заказ был оплачен)
def task_to_history(json_data):
  # key
  # order

  if get_key_by_value(platforms, key) != 'MAIN':
    return {'status': 'error', 'message': 'action incorrect'}, 404
  active_tasks = load_json(f"{filelink}/active_tasks.json")
  history_orders = load_json(f"{filelink}/history_tasks.json")

  history_orders[json_data['order']] = active_tasks[json_data['order']]
  del active_tasks[json_data['order']]

  save_json(active_tasks, f"{filelink}/active_tasks.json")
  save_json(history_orders, f"{filelink}/history_orders.json")

  return {'status': True}, 200 

dict_actions = {
  'check': (lambda json_data: check(json_data)),

  'create_order': (lambda json_data: create_order(json_data)),
  'cancel_order': (lambda json_data: cancel_order(json_data)),
  'change_order': (lambda json_data: change_order(json_data)),
  'check_order': (lambda json_data: check_order(json_data)),
  'check_orders': (lambda json_data: check_orders(json_data)),
  'get_social_info': (lambda json_data: get_social_info(json_data)),

  'get_task': (lambda json_data: get_task(json_data)),
  'send_complete_info': (lambda json_data: send_complete_info(json_data)),
  'send_start_task': (lambda json_data: send_start_task(json_data)),

  'task_to_history': (lambda json_data: task_to_history(json_data)),
}

class class_test(flask_restful.Resource):
  def post(self):
    json_data = flask.request.get_json(force=True)
    if 'key' not in json_data:
      return {'status': 'error', 'message': 'key not found'}, 404
    print(json_data['key'])
    if (
      json_data['key'] not in platforms.values() and
      json_data['key'] not in bots
      ):
      return {'status': 'error', 'message': 'key incorrect'}, 404
    if 'action' not in json_data:
      return {'status': 'error', 'message': 'action not found'}, 404
    if json_data['action'] not in dict_actions:
      return {'status': 'error', 'message': 'action incorrect'}, 404
    return dict_actions[json_data['action']](json_data)

if __name__ == '__main__':
  app = flask.Flask(__name__)
  api = flask_restful.Api(app)
  api.add_resource(class_test, '/', '//')
  # app.run(host = '0.0.0.0', port = 5000 ,debug=True, ssl_context=('cert.pem', 'key.pem'))
  app.run(host = '0.0.0.0', port = 5000 ,debug=True)