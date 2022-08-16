#!/usr/bin/env python3

import requests
import argparse
from bs4 import BeautifulSoup


def userFlags():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="File with card ID's on each line")
    parser.add_argument("-i", "--input", type=str, nargs='+', help="Input from terminal")
    parser.add_argument("-p", "--pretty", action='store_true', help="Prettify the output")
    return parser.parse_args()


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


def getName(cardHtml):
    soup = BeautifulSoup(cardHtml, "html.parser")
    cardName = soup.find_all("p", {"class": "rubrik"}).pop().get_text().split("\n")[0]
    return cardName


def getSellers(cardId):
    cardUrl = urlCreator(cardId)
    cardHtml = getCardHtml(cardUrl)

    name = getName(cardHtml)
    sellers = parseSellers(cardHtml)

    return sellers, name


def groupSellers(sellers, groupedSellers, cardId, cardName):
    for seller in sellers:
        if seller not in groupedSellers.keys():
            groupedSellers[seller] = {}
            groupedSellers[seller]["matches"] = 1
            matched = {"cardId": cardId, "cardName": cardName}
            groupedSellers[seller]["cards"] = [matched]
        elif cardId not in groupedSellers[seller]["cards"]:
            groupedSellers[seller]["matches"] += 1
            matched = {"cardId": cardId, "cardName": cardName}
            groupedSellers[seller]["cards"].append(matched)
    return groupedSellers


def findBestCombo(haveData, cards):
    filtered = {}
    found = []

    for seller in sorted(haveData, key=lambda key: haveData[key]["matches"], reverse=True):
        for card in haveData[seller]["cards"]:
            if card["cardId"] not in found:
                if seller not in filtered.keys():
                    filtered[seller] = []
                filtered[seller].append(card)
                found.append(card["cardId"])

    return filtered


def loadFile(fileName):
    cards = None
    with open(fileName) as f:
        cards = f.read().splitlines()
    return [int(card) for card in cards]


def prettifyOutput(output):
    for user in output.keys():
        print("{}".format(user))
        for card in output[user]:
            print("\t{} => {}".format(card["cardId"], card["cardName"]))
        


if __name__ == "__main__":
    groupedSellers = {}
    cards = None

    args = userFlags()

    if args.file != None:
        cards = loadFile(args.file)
    elif args.input != None:
        cards = [int(card) for card in args.input]

    if cards == None:
        exit(1)
    
    for card in cards:
        sellers, cardName = getSellers(card)
        groupedSellers = groupSellers(sellers, groupedSellers, card, cardName)

    output = findBestCombo(groupedSellers, cards)

    if args.pretty:
        prettifyOutput(output)
    else:
        print(output)
