#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup


def urlCreator(cardId):
    return "https://www.svenskamagic.com/kortparmen/index.php?cardid={}&expkvittar=true".format(cardId)


def getCardHtml(cardUrl):
    return requests.get(cardUrl).text


def parseSellers(cardHtml):
    soup = BeautifulSoup(cardHtml, "html.parser")
    match = soup.find_all("div", {"class": "box rod"}).pop()
    sellers = []
    for seller in match.find_all("b"):
        sellers.append(seller.get_text())
    return sellers

# TODO: Link name to 
def getName(cardId):
    cardUrl = urlCreator(cardId)
    cardHtml = getCardHtml(cardUrl)
    soup = BeautifulSoup(cardHtml, "html.parser")
    cardName = soup.find_all("p", {"class": "rubrik"}).pop().get_text()
    return cardName


def getSellers(cardId):
    cardUrl = urlCreator(cardId)
    cardHtml = getCardHtml(cardUrl)
    sellers = parseSellers(cardHtml)
    return sellers


def groupSellers(sellers, groupedSellers, cardId):
    for seller in sellers:
        if seller not in groupedSellers.keys():
            groupedSellers[seller] = {}
            groupedSellers[seller]["matches"] = 1
            groupedSellers[seller]["cards"] = [cardId]
        elif cardId not in groupedSellers[seller]["cards"]:
            groupedSellers[seller]["matches"] += 1
            groupedSellers[seller]["cards"].append(cardId)
    return groupedSellers


def findBestCombo(haveData, cards):
    filtered = {}
    found = []

    for seller in sorted(haveData, key=lambda key: haveData[key]["matches"], reverse=True):
        for card in haveData[seller]["cards"]:
            if card not in found:
                if seller not in filtered.keys():
                    filtered[seller] = []
                filtered[seller].append(card)
                found.append(card)

    return filtered


if __name__ == "__main__":
    groupedSellers = {}
    cards = [48269, 57696, 61740, 59110, 62031, 43751, 51860, 49324, 48170, 56972, 41577, 61148, 38227]

    for card in cards:
        sellers = getSellers(card)
        groupedSellers = groupSellers(sellers, groupedSellers, card)

    print(findBestCombo(groupedSellers, cards))
