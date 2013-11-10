#!/usr/bin/env python
# -*- coding: utf-8 -*-

import feedparser
import re

    
# RSSフィードのタイトルと、単語の頻度のディクショナリを返す
def getwordcounts(url):
    # フィードをパースする
    d = feedparser.parse(url)
    wc = {}

    # すべてのエントリをループする
    for e in d.entries:
        if 'summary' in e: summary=e.summary
        else: summary = e.description

    # 単語のリストを取り出す
    words = getwords(e.title+' '+summary)
    for word in words:
        wc.setdefault(word,0)
        wc[word] += 1

    return d.feed.title,wc


def getwords(html):
    # すべてのHTMLタグを取り除く
    txt = re.compile(r'<[^>+>').sub('', html)

    # すべての非アルファベット文字で分割する
    words = re.compile(r'[^A-Za-z]+').split(txt)

    # 小文字に変換する
    return [word.lower() for word in words if word != '']

apcount = {}
wordcounts = {}
feedlist = [line for line in file('feedlist.txt')]
for feedurl in feedlist:
    try:
        title, wc = getwordcounts(feedurl)
        wordcounts[title] = wc
        for word, count in wc.items():
            apcount.setdefault(word, 0)
            if count > 1:
                apcount[word] += 1
    except:
        print 'Failed to parse feed %s' % feedurl

wordlist = []
for w, bc in apcount.items():
    frac=float(bc)/len(feedlist)
    if frac>0.1 and frac<0.5:
        wordlist.append(w)

out=file('blogdata1.txt','w')
out.write('Blog')
for word in wordlist: out.write('\t%s' % word)
out.write('\n')
for blog,wc in wordcounts.items():
    print blog
    out.write(blog)
    for word in wordlist:
        if word in wc: out.write('\t%d' % wc[word])
        else: out.write('\t0')
    out.write('\n')
        
