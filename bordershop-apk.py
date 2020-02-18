# coding: latin-1

from bs4 import BeautifulSoup
from urllib2 import urlopen
import re

def make_soup(url):
    html = urlopen(url).read()
    soup = BeautifulSoup(html, "lxml")
    return soup


url = raw_input("https://www.bordershop.com/se")
print url
s = make_soup(url)
menu = s.find("div", class_ = "topmenuinner")
categories = []
categories.append((menu.find("a", string = re.compile("\xd6l", re.IGNORECASE)), 0.045)) #In quest of beer. \xd6 => Ö
categories.append((menu.find("a", string = re.compile("sprit", re.IGNORECASE)), 0.35))
categories.append((menu.find("a", string = re.compile("vin", re.IGNORECASE)), 0.1))
categories.append((menu.find("a", string = re.compile("Lik\xf6r", re.IGNORECASE)), 0.15))

total = []
for obj in categories:
    cat = obj[0]
    default_conc = obj[1]
    link = url + cat["href"] + "?page=1&hits=1000#" #view all items in a category on a single page
    cat_name = cat.string
    soup = make_soup(link)
    plist = soup.find("div", id = "ProductsList")
    results = plist.find_all("div", class_ = "search_result")
    values = []
    for res in results:
        try:
            title = unicode(res.h3.a.string)
        except:
            continue
        perc_in_string = title.find("%")
        if perc_in_string > 0:
            strip_title = title[:perc_in_string].rstrip()
            split_title = strip_title.split(" ")
            conc = 0.01 * float(re.sub("," , "." ,re.sub("[^\d,]" , "", split_title[-1])))
        else:
            conc = default_conc
        price_objects = res.find_all(class_ = re.compile("SEK"))
        price_string = price_objects[-1].string
        price = float(re.sub("," , "." ,re.sub("[^\d,]" , "" , price_string)))
        quant_strings = res.h4.string.split(" ")
        vol = 0
        try:
            vol_indices = [i - 1 for i,x in enumerate(quant_strings) if re.sub(".", "", x.lower) == "cl"]
        except:
            continue
        for index in vol_indices:
            vol += int(re.sub("\D", "" , quant_strings[index]))
        quantity = 1
        for index, line in enumerate(quant_strings):
            if index not in vol_indices:
                try:
                    quantity = int(re.sub("\D", "" , line))
                except:
                    pass
        apk = conc * quantity * vol / price
        values.append((title,apk,conc,price,quantity,vol))
    total += values
    sorted_list = sorted(values, key=lambda x: x[1], reverse=True)
    apk, conc, price, vol = (0,)*4
    quantity = 1
    for val in sorted_list:
        apk += val[1]
        conc += val[2]
        price += val[3]
        vol += val[4]*val[5]
    length = len(sorted_list)
    try:
        apk /= length
        conc /= length
        price /= length
        vol /= length
        sorted_list.append(("Averages",apk,conc,price,quantity,vol))
    except:
        continue
    it = 1
    print cat_name + ":"
    for val in sorted_list:
        print "{0:3d}".format(it) + ": " + val[0].ljust(40, ".") + "APK: " + "{0:.5f}".format(val[1]) + "\tConcentration: " + str(100*val[2]) + "%\tPrice: " + str(val[3]) + ":-\tQuantity: " + str(val[4]) + "\tSize: " + str(val[5]) + "cl"
        it += 1
    print "-" * 50
    print ""

sorted_total = sorted(total, key=lambda x: x[1], reverse=True)
it = 1
print "Total:"
for val in total:
    print "{0:3d}".format(it) + ": " + val[0].ljust(40, ".") + "APK: " + "{0:.5f}".format(val[1]) + "\tConcentration: " + str(100*val[2]) + "%\tPrice: " + str(val[3]) + ":-\tQuantity: " + str(val[4]) + "\tSize: " + str(val[5]) + "cl"
    it += 1
print "-" * 50
print ""
