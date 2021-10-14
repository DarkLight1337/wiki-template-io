import argparse
from itertools import zip_longest
from pathlib import Path

from utils import (
    read_df, read_wikicode,
    get_full_page_names_col,
    write_df, write_wikicode,
    make_row,
    get_templates_in_df, get_templates_in_wikicode,
)


def list_pages(template_name: str) -> None:
    df = read_df(template_name)

    for full_page_name in set(get_full_page_names_col(df)):
        print(full_page_name)

def push_template(wikitext_file: Path, template_name: str, full_page_name: str) -> None:
    wikicode = read_wikicode(wikitext_file)
    df = read_df(template_name)

    orig_templates = get_templates_in_wikicode(wikicode, template_name)
    new_templates = get_templates_in_df(df, full_page_name, template_name)

    # Update the wikicode
    empty = object()
    for orig_t, new_t in zip_longest(orig_templates, new_templates, fillvalue=empty):
        if orig_t != empty and new_t != empty:
            wikicode.replace(orig_t, new_t)
        elif orig_t == empty and new_t != empty:
            wikicode.append(new_t)
        elif orig_t != empty and new_t == empty:
            wikicode.remove(orig_t)

    write_wikicode(wikicode, wikitext_file)

def pull_template(wikitext_file: Path, template_name: str, full_page_name: str) -> None:
    wikicode = read_wikicode(wikitext_file)
    df = read_df(template_name)

    # Update the dataframe
    df = df[get_full_page_names_col(df) != full_page_name]
    df = df.append([
        make_row(full_page_name, i, t)
        for i, t in enumerate(get_templates_in_wikicode(wikicode, template_name))
    ])

    write_df(df, template_name)


if __name__ == '__main__':
    main_parser = argparse.ArgumentParser(
        description='Process a template in a wikipedia article.',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = main_parser.add_subparsers(title='subcommands')

    list_pages_parser = subparsers.add_parser('list-pages', help='List pages containing a template')
    list_pages_parser.add_argument('template_name', metavar='<template_name>', type=str, help='The name of the template to process')
    list_pages_parser.set_defaults(func=lambda args: list_pages(args.template_name))

    push_parser = subparsers.add_parser('push', help='Push a template to the wiki')
    pull_parser = subparsers.add_parser('pull', help='Pull a template from the wiki')

    for parser in (push_parser, pull_parser):
        parser.add_argument('template_name', metavar='<template_name>', type=str, help='The name of the template to process')
        parser.add_argument('full_page_name', metavar='<full_page_name>', type=str, help='The {{FULLPAGENAME}} of the article containing the wikitext')
        parser.add_argument('wikitext_file', metavar='<wikitext_file>', type=Path, help='The path to the file containing the wikitext')

    push_parser.set_defaults(
        func=lambda args: push_template(args.wikitext_file, args.template_name, args.full_page_name),
    )
    pull_parser.set_defaults(
        func=lambda args: pull_template(args.wikitext_file, args.template_name, args.full_page_name),
    )

    args = main_parser.parse_args()
    args.func(args)
