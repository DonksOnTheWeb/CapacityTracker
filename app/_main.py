from _readers import readFromGeneric
import datetime
from datetime import timedelta

from _writers import writeAverages
from _writers import writeHistoric


def mainLoop():
    howFarBack = 21

    data = readAll()
    averages = calculateAverageImplied(data, howFarBack)
    writeAverages(averages, "21 Day Weighted Average")
    writeHistoric(data, howFarBack, 'Ambient')
    writeHistoric(data, howFarBack, 'Chilled')
    writeHistoric(data, howFarBack, 'Frozen')


def readAll():
    dataLump = readFromGeneric('Coefficient Dump', '11-DCc6jBqsNfSMFqzxSvN7RFxk2R-EVpzAh2kLIMcyM', '!B:L')
    dataLump = dataLump[2:]

    startFrom = datetime.datetime.strptime('2022-08-12', '%Y-%m-%d')

    data = {}
    bookends = {}

    for entry in dataLump:
        dte = datetime.datetime.strptime(entry[0], '%Y-%m-%d')
        if dte >= startFrom:
            mfc = entry[1]
            if len(entry[2].strip()) > 0:
                ambient_implied = calcImplied(entry[2], entry[3], entry[4])
                chilled_implied = calcImplied(entry[5], entry[6], entry[7])
                frozen_implied = calcImplied(entry[8], entry[9], entry[10])

                local = {'Ambient': ambient_implied, 'Chilled': chilled_implied, 'Frozen': frozen_implied}

                if mfc in data:
                    data[mfc][dte] = local
                else:
                    data[mfc] = {dte: local}

                if mfc in bookends:
                    if 'Earliest' in bookends[mfc]:
                        if dte < bookends[mfc]['Earliest']:
                            bookends[mfc]['Earliest'] = dte
                        if dte > bookends[mfc]['Latest']:
                            bookends[mfc]['Latest'] = dte
                else:
                    bookends[mfc] = {'Earliest': dte, 'Latest': dte}
    return {'Data': data, 'Bookends': bookends}


def calcImplied(coefficient, nominal, used):
    coefficient = float(coefficient.replace('%', '')) / 100.0
    nominal = float(nominal)
    used = float(used)

    constant = 0.55

    calculated = (used / nominal)
    confirmed = calculated + coefficient
    implied = (used / confirmed) / (nominal / constant)

    return implied


def calculateAverageImplied(data, howFarBack):
    implied = data['Data']
    Bookends = data['Bookends']

    results = {}

    for mfc in implied:
        earliest = Bookends[mfc]['Earliest']
        latest = Bookends[mfc]['Latest']

        cutoff = latest - timedelta(days=howFarBack)

        if cutoff < earliest:
            cutoff = earliest

        diff = (latest - cutoff).days

        ambient = 0
        chilled = 0
        frozen = 0
        itr = 0
        for dte in implied[mfc]:
            if dte >= cutoff:
                weight = diff - (latest - dte).days + 1
                ambient = ambient + (implied[mfc][dte]['Ambient'] * weight)
                chilled = chilled + (implied[mfc][dte]['Chilled'] * weight)
                frozen = frozen + (implied[mfc][dte]['Frozen'] * weight)
                itr = itr + weight

        ambient = ambient / itr
        chilled = chilled / itr
        frozen = frozen / itr

        results[mfc] = {'Ambient': ambient, 'Chilled': chilled, 'Frozen': frozen}

    return results
