import logging
import os
import time
from itertools import count, islice
from functools import reduce
from collections import defaultdict

# Postgres specific queries should go into separate module.
from django.contrib.postgres.aggregates import StringAgg
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

from django.conf import settings
from django.utils.text import smart_split
from django.db.models import Q
from whoosh import writing
from whoosh.analysis import StemmingAnalyzer

from whoosh.qparser import MultifieldParser, OrGroup
from whoosh.sorting import FieldFacet, ScoreFacet
from whoosh.writing import AsyncWriter
from whoosh.searching import Results

from whoosh.qparser import MultifieldParser, OrGroup
from whoosh.analysis import STOP_WORDS
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import ID, TEXT, KEYWORD, Schema, BOOLEAN, NUMERIC, DATETIME

from .models import Post

logger = logging.getLogger('biostar')

# Stop words ignored where searching.
STOP = ['there', 'where', 'who'] + [w for w in STOP_WORDS]
STOP = set(STOP)

def timer_func():
    """
    Prints progress on inserting elements.
    """

    last = time.time()

    def elapsed(msg):
        nonlocal last
        now = time.time()
        sec = round(now - last, 1)
        last = now
        print(f"{msg} in {sec} seconds")

    def progress(index, step=500, total=0, msg=""):
        nonlocal last
        if index % step == 0:
            percent = int((index / total) * 100) if total >= index else index
            elapsed(f"... {percent}% ({index} out of {total}). {step} {msg}")

    return elapsed, progress


class SearchResult(object):
    def __init__(self, **kwargs):
        self.title = ''
        self.content = ''
        self.url = ''
        self.type_display = ''
        self.content_length = ''
        self.type = ''
        self.lastedit_date = ''
        self.is_toplevel = ''
        self.rank = ''
        self.uid = ''
        self.author_handle = ''
        self.author = ''
        self.author_email = ''
        self.author_score = ''
        self.thread_votecount = ''
        self.vote_count = ''
        self.author_uid = ''
        self.author_url = ''
        self.__dict__.update(kwargs)


def close(r):
    # Ensure the searcher object gets closed.
    r.searcher.close() if isinstance(r, Results) else None
    return


def parse_result(result):
    "Return a bunch object for result."

    # Result is a database object.
    if isinstance(result, Post):
        bunched = SearchResult(title=result.title, content=result.content, url=result.get_absolute_url(),
                               type_display=result.get_type_display(), content_length=len(result.content),
                               type=result.type, lastedit_date=result.lastedit_date, is_toplevel=result.is_toplevel,
                               rank=result.rank, uid=result.uid, author_handle=result.author.username,
                               author=result.author.profile.name, author_email=result.author.email,
                               author_score=result.author.profile.score, thread_votecount=result.thread_votecount,
                               vote_count=result.vote_count, author_uid=result.author.profile.uid,
                               author_url=result.author.profile.get_absolute_url())

    # Result is a dictionary returned from indexed searched
    else:
        bunched = SearchResult(title=result['title'], content=result['content'], url=result['url'],
                               type_display=result['type_display'], content_length=result['content_length'],
                               type=result['type'], lastedit_date=result['lastedit_date'],
                               is_toplevel=result['is_toplevel'], rank=result['rank'], uid=result['uid'],
                               author_handle=result['author_handle'], author=result['author'],
                               author_score=result['author_score'],
                               thread_votecount=result['thread_votecount'], vote_count=result['vote_count'],
                               author_uid=result['author_uid'], author_url=result['author_url'])

    return bunched


def index_exists():
    return exists_in(dirname=settings.INDEX_DIR, indexname=settings.INDEX_NAME)


def add_index(post, writer):
    writer.update_document(title=post.title, url=post.get_absolute_url(),
                           type_display=post.get_type_display(),
                           content_length=len(post.content),
                           type=post.type,
                           lastedit_date=post.lastedit_date,
                           content=post.content, tags=post.tag_val,
                           is_toplevel=post.is_toplevel,
                           rank=post.rank, uid=post.uid,
                           author_handle=post.author.username,
                           author=post.author.profile.name,
                           author_email=post.author.email,
                           author_score=post.author.profile.score,
                           thread_votecount=post.thread_votecount,
                           vote_count=post.vote_count,
                           author_uid=post.author.profile.uid,
                           author_url=post.author.profile.get_absolute_url())


def get_schema():
    analyzer = StemmingAnalyzer(stoplist=STOP)
    schema = Schema(title=TEXT(stored=True, analyzer=analyzer, sortable=True),
                    url=ID(stored=True),
                    content_length=NUMERIC(stored=True, sortable=True),
                    thread_votecount=NUMERIC(stored=True, sortable=True),
                    vote_count=NUMERIC(stored=True, sortable=True),
                    content=TEXT(stored=True, analyzer=analyzer, sortable=True),
                    tags=KEYWORD(stored=True, commas=True),
                    is_toplevel=BOOLEAN(stored=True),
                    lastedit_date=DATETIME(stored=True, sortable=True),
                    rank=NUMERIC(stored=True, sortable=True),
                    author=TEXT(stored=True),
                    author_score=NUMERIC(stored=True, sortable=True),
                    author_handle=TEXT(stored=True),
                    author_email=TEXT(stored=True),
                    author_uid=ID(stored=True),
                    author_url=ID(stored=True),
                    uid=ID(stored=True),
                    type=NUMERIC(stored=True, sortable=True),
                    type_display=TEXT(stored=True))
    return schema


def init_index():
    # Initialize a new index or return an already existing one.

    if index_exists():
        ix = open_dir(dirname=settings.INDEX_DIR, indexname=settings.INDEX_NAME)
    else:
        # Ensure index directory exists.
        os.makedirs(settings.INDEX_DIR, exist_ok=True)
        ix = create_in(dirname=settings.INDEX_DIR, schema=get_schema(), indexname=settings.INDEX_NAME)

    return ix


def print_info():
    """
    Prints information on the index.
    """
    ix = init_index()

    counter = defaultdict(int)
    for index, fields in enumerate(ix.searcher().all_stored_fields()):
        key = fields['type_display']
        counter[key] += 1

    total = 0
    print('-' * 20)
    for key, value in counter.items():
        total += value
        print(f"{value}\t{key}")
    print('-' * 20)
    print(f"{total} total posts")


def index_posts(posts, overwrite=False):
    """
    Create or update a search index of posts.
    """

    ix = init_index()
    # The writer is asynchronous by default
    writer = AsyncWriter(ix)

    elapsed, progress = timer_func()
    total = posts.count()
    stream = islice(zip(count(1), posts), None)

    # Loop through posts and add to index
    for step, post in stream:
        progress(step, total=total, msg="posts indexed")
        add_index(post=post, writer=writer)

    # Commit to index
    if overwrite:
        logger.info("Overwriting the old index")
        writer.commit(mergetype=writing.CLEAR)
    else:
        writer.commit()

    elapsed(f"Indexed posts={total}")


def crawl(reindex=False, overwrite=False, limit=1000):
    """
    Crawl through posts in batches and add them to index.
    """

    if reindex:
        logger.info(f"Setting indexed field to false on all post.")
        Post.objects.filter(indexed=True).exclude(root=None).update(indexed=False)

    # Index a limited number of posts at one time.
    posts = Post.objects.exclude(root=None, indexed=False)[:limit]

    try:
        # Add post to search index.
        index_posts(posts=posts, overwrite=overwrite)
    except Exception as exc:
        logger.error(f'Error updating index: {exc}')
        Post.objects.filter(id__in=posts.values('id')).update(indexed=False)

    # Set the indexed field to true
    Post.objects.filter(id__in=posts.values('id')).update(indexed=True)

    return


def sql_search(query, fields=None):
    """search_fields example: ['name', 'category__name', '@description', '=id']
    """

    query_string = query.strip()

    filters = []

    query_list = [s for s in smart_split(query_string) if s not in STOP]
    for bit in query_list:
        queries = [Q(**{f"{field_name}__icontains": bit}) for field_name in fields]
        filters.append(reduce(Q.__or__, queries))

    filters = reduce(Q.__and__, filters) if len(filters) else Q(pk=None)

    results = Post.objects.filter(filters)
    logger.info("Preform sql lite search.")
    return results


def postgres_search(query, fields=None):
    query_string = query.strip()

    vector = reduce(SearchVector.__add__, [SearchVector(f) for f in fields])

    # List of Q() filters used to preform search
    filters = reduce(SearchQuery.__or__, [SearchQuery(s) for s in smart_split(query_string)])

    # print(filters, "filters", "*"*10)
    # vector = SearchVector('title') + SearchVector('content')

    results = Post.objects.annotate(search=vector).filter(search=filters)
    logger.info("Preform postgres search.")

    return results


def preform_whoosh_search(query, fields=None, page=None, per_page=20, **kwargs):
    """
        Query the indexed, looking for a match in the specified fields.
        Results a tuple of results and an open searcher object.
        """

    # Do not preform search if the index does not exist.
    if not index_exists() or len(query) < settings.SEARCH_CHAR_MIN:
        return []
    fields = fields or ['tags', 'title', 'author', 'author_uid', 'author_handle']
    ix = init_index()
    searcher = ix.searcher()

    # profile_score = FieldFacet("author_score", reverse=True)
    # post_type = FieldFacet("type")
    # thread = FieldFacet('thread_votecount')
    # # content_length = FieldFacet("content_length", reverse=True)
    # rank = FieldFacet("rank", reverse=True)
    # default = ScoreFacet()

    # Splits the query into words and applies
    # and OR filter, eg. 'foo bar' == 'foo OR bar'
    orgroup = OrGroup

    # sort_by = sort_by or [post_type, rank, thread, default, profile_score]
    # sort_by = [lastedit_date]

    parser = MultifieldParser(fieldnames=fields, schema=ix.schema, group=orgroup).parse(query)
    if page:
        # Return a pagenated version of the results.
        results = searcher.search_page(parser, pagenum=page, pagelen=per_page, sortedby=["lastedit_date"],
                                       reverse=True,
                                       terms=True, **kwargs)
        results.results.fragmenter.maxchars = 100
        # results.fragmenter.charlimit = None
        # Show more context before and after
        results.results.fragmenter.surround = 100
    else:
        results = searcher.search(parser, limit=settings.SEARCH_LIMIT, terms=True, **kwargs)
        # Allow larger fragments
        results.fragmenter.maxchars = 100
        # results.fragmenter.charlimit = None
        # Show more context before and after
        results.fragmenter.surround = 100

    # Sort results by last edit date.
    #results = sorted(results, key=lambda x: x['lastedit_date'])

    logger.info("Preformed index search")

    return results


def preform_db_search(query='', fields=None, filter_for=Q()):
    """
    Preform a db search
    """

    if 'postgres' in settings.DATABASES['default']['ENGINE']:
        # Preform search using postgres
        results = postgres_search(query=query, fields=fields)
    else:
        # Preform search using sql lite.
        results = sql_search(query=query, fields=fields)

    results = results.filter(filter_for)
    results = results.order_by('type', '-lastedit_date', '-rank')
    results = results[:settings.SEARCH_LIMIT]

    logger.info("Preformed db query.")
    return results


def more_like_this(uid, db_search=False):
    """
    Return posts similar to the uid given.
    """

    # if db_search:
    #     # Get the post of interest
    #     post = Post.objects.filter(uid=uid).first()
    #     # Search for posts with similar content to current one.
    #     content = post.content if post else ''
    #     filter_for = Q(is_toplevel=True)
    #     results = preform_db_search(query=content, fields=['content'], filter_for=filter_for)
    # else:
    results = preform_whoosh_search(query=uid, fields=['uid'])
    if len(results):
        results = results[0].more_like_this("content", top=settings.SIMILAR_FEED_COUNT)
        # Filter results for toplevel posts.
        results = filter(lambda p: p['is_toplevel'] is True, results)

    # Ensure results types stay consistent.
    final_results = list(map(parse_result, results))
    if isinstance(results, Results):
        # Ensure searcher object gets closed.
        close(results)

    return final_results


def map_db_fields(fields):
    """
    Map search fields to database appropriate values.
    """
    db_map = dict(author_handle='author__username',
                  author_score='author__profile__score',
                  author_email='author__email',
                  author_uid='author__profile__uid',
                  tags='tag_val'
                  )

    fields = [db_map.get(f, f) for f in fields]

    return fields


def preform_search(query, fields=None, db_search=False):
    fields = fields or ['tags', 'title', 'author', 'author_uid', 'author_handle']

    if db_search:
        # Preform a full text search on database.
        fields = map_db_fields(fields)
        results = preform_db_search(query=query, fields=fields)
    else:
        # Preform search on indexed posts.
        results = preform_whoosh_search(query=query, fields=fields)

    # Ensure returned results types stay consistent.
    final_results = list(map(parse_result, results))
    if isinstance(results, Results):
        # Ensure searcher object gets closed.
        close(results)

    return final_results
