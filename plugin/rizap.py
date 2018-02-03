# -*- coding: utf-8 -*-
from slackbot.bot import respond_to
from slackbot.bot import listen_to
import datetime
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import re
import pandas as pd
import os
from pprint import pprint


### bot method
@listen_to('グラフ')
def graph(message):
    message.reply('グラフを表示します．')
    users = message.channel._client.users
    print("===========================================================")
    # names = [user["real_name"] for k,user in users.items() if user['is_bot'] != True and user['name'] != 'slackbot']
    names = ["hiromu","yui"]
    dfs = [_create_df(name) for name in names]
    dfs = list(map(_add_change_cols, dfs))
    print(dfs)
    df_merged = dfs[0].join(dfs[1:], how='outer')
    print(df_merged)
    plt.style.use('seaborn-pastel')
    ax = df_merged.plot(y=['hiromu','yui'], ylim=[-10,10], style=['-o','-o'])
    ax.xaxis.set_major_locator(dates.DayLocator(interval=2))
    # set formatter
    ax.xaxis.set_major_formatter(dates.DateFormatter('%m/%d\n%a'))
    # set font and rotation for date tick labels
    plt.gcf().autofmt_xdate()

    plt.savefig("graph/all.png")

    cwd = os.path.abspath(os.path.dirname(__file__))
    fname = os.path.join(cwd, '../graph/all.png')

    message.channel.upload_file("graph.png", fname)


@respond_to('グラフ')
def personal_graph(message):
    name = _username(message)
    df = _create_df(name)
    message.reply('{}のグラフ作るけん，ちょいまち！'.format(name))

    plt.style.use('seaborn-pastel')

    ax = df.plot(y='weight_{}'.format(name), style=['-o'])
    ax.xaxis.set_major_locator(dates.DayLocator(interval=2))
    # set formatter
    ax.xaxis.set_major_formatter(dates.DateFormatter('%m/%d\n%a'))
    # set font and rotation for date tick labels
    plt.gcf().autofmt_xdate()

    plt.savefig("graph/{}.png".format(name))

    cwd = os.path.abspath(os.path.dirname(__file__))
    fname = os.path.join(cwd, '../graph/{}.png'.format(name))

    message.channel.upload_file("graph.png", fname)


@respond_to('記録')
def history(message):

    name = _username(message)
    df = _create_df(name)
    s = ""
    for l in df.itertuples(name=None):
        s = s + "{}: {}\n".format(l[0],l[1])

    message.reply(s)


@respond_to('(.*)を登録')
def regist(message, weight_str):

    num_reg= re.compile('\d+(?:\.\d+)?')
    if bool(num_reg.match(weight_str)):
        weight = float(weight_str)
        name = _username(message)
        today = datetime.date.today()

        f = open('db/{}.csv'.format(name), 'a')
        f.write("{0},{1}".format(today, weight))
        f.close()

        message.reply('{0}の{1}年{2}月{3}日の体重({4} kg) を登録しといたで:sunglasses:'.format(name, today.year, today.month, today.day, weight))
    else:
        message.reply('入力がちゃうがな:rage:')


#### praivate method
def _username(message):

    name = message.channel._client.users[message.body['user']]['profile']['display_name']
    if name == "":
        name = message.channel._client.users[message.body['user']]['real_name']
    return name


def _create_df(name):

    df = pd.read_csv('db/{}.csv'.format(name), names=('date','weight_{}'.format(name)))
    df = df.drop_duplicates(['date'], keep='last')
    df['date'] = pd.to_datetime(df['date']).map(lambda x: x.date())
    # df['date'] = pd.to_datetime(df['date'])
    # df = df.reset_index(drop=True)
    df = df.set_index('date')
    return df


def _add_change_cols(df):

    tmp = df.keys()[0]
    k = tmp[7:]
    df["{}".format(k)] = df['{}'.format(tmp)].map(lambda x: x - df['{}'.format(tmp)][0])
    return df
