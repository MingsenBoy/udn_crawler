import argparse
import datetime
from codebase.udn_urls import get_urls
from codebase.output import output_mysql
from codebase.output import output_mongo
from codebase.output import output_csv
from codebase.multi_thread import multi_crawling


def process_command():
    parser = argparse.ArgumentParser(prog=None, description='Scrape UDN news')

    parser.add_argument('--start_time', '-st', type=str, default="2014-01-01 00:00:00", help='Choose start time.', dest='st')
    parser.add_argument('--end_time', '-et', default=datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"),
                        type=str, help='Choose end time.', dest='et')
    parser.add_argument('--category', '-cg', default='all', type=str, help='Choose the category.', dest='cg')
    parser.add_argument('--output', '-op', default='mysql', type=str, help='Choose output format: mysql, mongo or csv.', dest='op')
    parser.add_argument('--path', '-pt', default='output/', type=str, help='Set the path for the saving data.', dest='pt')
    parser.add_argument('--mongoURI', '-mgu', default='mongodb://localhost:27017/', type=str,
                        help='Insert which Mongo URI.', dest='mgu')
    parser.add_argument('--mongodb', '-mgd', default='udn', type=str, help='Insert which Mongo Database.', dest='mgd')
    parser.add_argument('--mongocol', '-mgc', default='all', type=str, help='Insert which Mongo Collection.', dest='mgc')

    return parser.parse_args()


def udn_crawler_op_mysql(st, et, cg):
    links = get_urls(st, et, cg)
    results = multi_crawling(links)
    output_mysql(results)


def udn_crawler_op_mongo(st, et, cg, mgu, mgd, mgc):
    links = get_urls(st, et, cg)
    results = multi_crawling(links)
    output_mongo(mgu, mgd, mgc, results)


def udn_crawler_op_csv(st, et, cg, pt):
    links = get_urls(st, et, cg)
    results = multi_crawling(links)
    output_csv(results, st, et, pt)


if __name__ == '__main__':
    begin_time = datetime.datetime.now()
    args = process_command()
    if args.op == "mysql":
        udn_crawler_op_mysql(args.st, args.et, args.cg)
    elif args.op == "mongo":
        udn_crawler_op_mongo(args.st, args.et, args.cg, args.mgu, args.mgd, args.mgc)
    else:
        udn_crawler_op_csv(args.st, args.et, args.cg, args.pt)
    print("總花費時間:", datetime.datetime.now() - begin_time)
