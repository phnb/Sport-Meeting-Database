from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render
from django.db import connection

from django.db import models
import pymysql

# Create your views here.

event = {}
cursor = connection.cursor()


def listplayers(request):
    cursor.execute("select Player_id,Player_name,Gender,College_name from player")
    data = cursor.fetchall()
    return render(request, 'list_players.html', context={'data': data})


def sign(request):
    return render(request, 'register.html')



def analysis_display():
    cursor.execute("select College_name, par_records, par_people, Population, \
        (par_records*0.3+par_people*0.7)/(Population*0.7+4*Population*0.3) as \
        Engagement_rate from (with total_colls(College_name) as \
        (select College_name from player, event_has_player where \
            player.Player_id = event_has_player.Player_id AND Event_has_player.Event_round = 1)\
	    select count(*) as par_records, College_name from total_colls as records_coll group by College_name\
        ) as population_coll natural join (\
        select count(*) as par_people, College_name from (\
		with distinct_id(id) as (\
			select distinct Player_id from event_has_player)\
		select College_name from player, distinct_id where player.Player_id = distinct_id.id\
	    ) as popu_coll group by College_name\
        ) as records_coll\
        natural join (\
        	select College_name, Population from college\
        ) as total_coll_popu\
        ;")
    data = cursor.fetchall()
    return data


# 输入：无
# 数据库操作：在college_ranking中找出书院分数与排名
# 输出：输出{data:((college_name,score）,(college_name,score)...)}到'homepage.html'
def homepage(request):
    cursor.execute("select College_ranking, College_name, College_score \
        from College_rank natural join College order by College_ranking ASC")
    data = cursor.fetchall()
    return render(request, 'index.html', context={'data': data})


# 输入："event_name", "category", "round"
# 数据库操作：把对应的event_result选出来
# 输出 {'data': ((event_name, category, round, ranking, id, performance), ...)}到'event_result.html'
def event_result(request):
    event_name = request.POST['event_name']
    category = request.POST['category']
    Round = request.POST['round']
    cursor.execute("select Ranking, Id, Performance from Event_Result where Event_name = '%s' and \
        Event_category = '%s' and Event_round = %s order by Ranking" % (event_name, category, Round))
    data = cursor.fetchall()
    print(data)
    event_name = 'Eventname: ' + event_name
    category = 'Category: ' + category
    Round = 'Round: ' + Round
    return render(request, 'event_result.html', context={"event": (event_name, category, Round), 'data': data})


# 输入："id", "event_name"
# 数据库操作：检测是否这个id在player中已经存在，如果是，跳转到reminder.html。
#         如果否，在数据库中找到这个id的性别，默认round是1，然后在event_has_player中更新数据。跳转到success.html
# 输出：无
def signing(request):
    name = request.POST['event_name']
    ID = request.POST['id']
    cursor.execute("select Gender from sport_meeting_management_system.player where Player_id = %s" % (ID))
    gender = cursor.fetchall()
    if gender == ():
        return render(request, 'reminder.html')
    else:
        # print(gender)
        # print(gender[0])
        # print(gender[0][0])
        addTuple = (name, gender[0][0], 1, ID)
        insSta = "insert into sport_meeting_management_system.event_has_player values " + str(addTuple)
        # print(insSta)
        cursor.execute(insSta)
        return render(request, 'success.html')


# 输入："password"
# 数据库操作：无
# 输出：无
# 其他操作：查看password是否是我们预先设好的一个值，如果是则跳转到org.html,否则跳转到提示登录失败的网页
def check(request):
    correct_pw = '3170brotherhood'
    password = request.POST['password']
    if password == correct_pw:
        data = analysis_display()
        return render(request, 'org.html', context = {'data': data})
    else:
        return render(request, 'fail_log.html')


# 输入："event_name", "category", "round"
# 数据库操作：根据输入，找到这个比赛的所有报名选手
# 输出：传出{'data':((event_name,category, round, player_id, name),...)}到type_in.html
def find_event_information(request):
    global event
    event_name = request.POST['event_name']
    category = request.POST['category']
    Round = request.POST['round']
    cursor.execute("select Player_id, Player_name from event_has_player natural join player \
        where Event_name = '%s' and Event_category = '%s' and Event_round = %s" % (event_name, category, Round))
    data = cursor.fetchall()
    event = {'event_name': event_name, 'category': category, 'round': Round, 'data': data}
    return render(request, 'type_in.html', context={'data': data})


# 输入： "event_name", "category", "round", "id", "name", "performance", "ranking"， 除了前三个，其他都是数组
# 数据库操作： 将结果插入到数据库event_result里面。根据整个event_result表，更新college,college_ranking里的score
# 输出：无
def update_college_score():
    rank = [0, 10, 6, 3, 1, 1, 1, 1, 1]
    cursor.execute("select Ranking, Id from event_result where Event_round = 2")
    data = cursor.fetchall()
    print(data)
    diligentia = 0
    shaw = 0
    harmonia = 0
    muse = 0
    cursor.execute("UPDATE college SET College_score = 0")
    cursor.execute("delete from college_rank where College_score <> 0")

    for player in data:
        cursor.execute("select College_name from player where Player_id = %s" % (player[1]))
        college = cursor.fetchall()
        print("college:", college)
        print(college)
        if (college[0][0]).lower() == "diligentia":
            diligentia += rank[int(player[0])]
        elif (college[0][0]).lower() == "shaw":
            shaw += rank[int(player[0])]
        elif (college[0][0]).lower() == "harmonia":
            harmonia += rank[int(player[0])]
        elif (college[0][0]).lower() == "muse":
            muse += rank[int(player[0])]

    score_list = [diligentia, harmonia, muse, shaw]
    score_set = list(set(score_list))
    score_set.sort(reverse = True)

    print(score_set)

    r = 1
    for i in score_set:
        if i != 0:
            print(i, r)
            cursor.execute("insert into college_rank value(%d, %d) " % (i, r))
            r += 1

    cursor.execute("UPDATE college SET College_score = %d where College_name = 'Diligentia'" % (diligentia))
    cursor.execute("UPDATE college SET College_score = %d where College_name = 'Shaw'" % (shaw))
    cursor.execute("UPDATE college SET College_score = %d where College_name = 'Muse'" % (muse))
    cursor.execute("UPDATE college SET College_score = %d where College_name = 'Harmonia'" % (harmonia))


def update_result(request):
    global event
    performance = request.POST.getlist('performance')
    ranking = request.POST.getlist('ranking')
    eventname = event['event_name']
    category = event['category']
    round = int(event['round'])
    dat = event['data']
    # print(performance[0],eventname, category, round, dat[0][0])
    for i in range(len(performance)):
        cursor.execute("insert into Event_Result values (%s, %s, '%s', '%s', '%s', %d)" % (ranking[i], \
                                                                                           dat[i][0], performance[i],
                                                                                           eventname, category, round))
    sel = 0
    if round == 1:
        sel = 3
    elif round == 2:
        sel = 2
        update_college_score()
    elif round == 3:
        return render(request, "success_update.html")
    cursor.execute("select id from Event_Result where Ranking <= %d and Event_round = %d" % (sel, round))
    id = cursor.fetchall()
    round = round + 1
    print(id)
    print(round)
    for i in range(sel):
        cursor.execute("insert into Event_has_Player values ('%s', '%s', %d, %s)" % (eventname, category, \
                                                                                     round, id[i][0]))
    return render(request, "success_update.html")


def player(request):
    return render(request, 'player.html')


def toregister(request):
    return render(request, 'register.html')


def org_log(request):
    return render(request, 'org_log.html')


def register(request):
    if request.method == 'POST':
        student_id = request.POST['id']
        name = request.POST['name']
        gender = request.POST['gender']
        college = request.POST['college']

        instruction = "insert into player (`Player_id`, `Player_name`, `Gender`, `College_name`) " \
                      "values(" + "'" + str(student_id) + "'" + "," + "'" + str(name) + "'" + "," + "'" + str(
            gender) + "'" + "," + "'" + str(college) + "'" + ")"
        print(instruction)
        cursor.execute(instruction)
    else:
        return HttpResponse('please visit us with POST')
    return render(request, 'success.html')