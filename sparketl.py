
from pyspark import SparkContext
from collections import OrderedDict

if __name__ == "__main__":
    sc = SparkContext(appName="challenge")
    lines=sc.textFile('spapp.txt')

    tuples = lines.map(lambda x: (x.split("|")))

    n = tuples.count()
    print '# row: ', n
    rows = tuples.take(n-1)[1:]
    map = OrderedDict()
    for row in rows:
        map[row[1]] = row[2].split(',')
        print row
    print map
    g = open('spapp.etl', 'w')
    for key in map:
        pages = map[key]
        for page in pages:
            print '|%s|%s' % (key, page.strip())
            g.write('|%s|%s\n' % (key, page.strip()))
    g.close()
    sc.stop()

