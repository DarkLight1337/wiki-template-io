from ast import literal_eval
from pathlib import Path
from typing import Iterable, Optional, Tuple

import pandas as pd

import mwparserfromhell
from mwparserfromhell.wikicode import Wikicode
from mwparserfromhell.nodes.template import Parameter, Template


DATA_DIR = Path(__file__).parent / 'data'
FULL_PAGE_NAME_COL = '_pageName'
INDEX_IN_PAGE_COL = '_indexInPage'

def get_filepath_and_sheet_name(template_name: str) -> Tuple[Path, Optional[str]]:
    template_name = template_name.strip()

    if template_name.startswith('Template:'):
        template_name = template_name.replace('Template:', '', 1)

    if '/' in template_name:
        name, suffix = template_name.split('/', maxsplit=1)
    else:
        name, suffix = template_name, None

    filepath = DATA_DIR / f'{name}.xlsx'
    sheet_name = suffix

    return filepath, sheet_name

def read_df(template_name: str) -> pd.DataFrame:
    filepath, sheet_name = get_filepath_and_sheet_name(template_name)
    if not filepath.exists():
        return pd.DataFrame(columns=[FULL_PAGE_NAME_COL, INDEX_IN_PAGE_COL])

    if sheet_name is None:
        sheet_name = 0

    return pd.read_excel(str(filepath), sheet_name=sheet_name, dtype=object, engine='openpyxl')

def get_full_page_names_col(df: pd.DataFrame) -> pd.Series:
    return df[FULL_PAGE_NAME_COL]

def write_df(df: pd.DataFrame, template_name: str) -> None:
    filepath, sheet_name = get_filepath_and_sheet_name(template_name)
    if sheet_name is None:
        sheet_name = 'Sheet1'

    # Check for duplicates
    df.set_index([FULL_PAGE_NAME_COL, INDEX_IN_PAGE_COL], verify_integrity=True)

    df.to_excel(filepath, sheet_name=sheet_name, index=False, engine='openpyxl')


def read_wikicode(file: Path) -> Wikicode:
    wikitext = file.read_text()
    return mwparserfromhell.parse(wikitext, skip_style_tags=True)

def write_wikicode(wikicode: Wikicode, file: Path) -> None:
    file.write_text(str(wikicode))


def make_row(full_page_name: str, index_in_page: int, template: Template) -> pd.Series:
    def convert_wikicode(wikicode: Wikicode):
        s = str(wikicode).strip()
        try:
            v = literal_eval(s)
            return v if isinstance(v, (float, int)) else s
        except Exception:
            return s

    data = {convert_wikicode(p.name): convert_wikicode(p.value) for p in template.params}
    return pd.Series({**data, FULL_PAGE_NAME_COL: full_page_name, INDEX_IN_PAGE_COL: index_in_page})

def make_template(row: pd.Series, template_name: str) -> Template:
    return Template(
        f'{template_name}\n ',
        params=[
            Parameter(f' {k} ', f' {v}\n ') for k, v in row.items()
            if k not in (FULL_PAGE_NAME_COL, INDEX_IN_PAGE_COL) and not pd.isna(k) and not pd.isna(v)
        ],
    )


def get_templates_in_df(df: pd.DataFrame, full_page_name: str, template_name: str) -> Iterable[Template]:
    return (
        make_template(row, template_name)
        for _, row in df[get_full_page_names_col(df) == full_page_name].iterrows()
    )

def get_templates_in_wikicode(wikicode: Wikicode, template_name: str) -> Iterable[Template]:
    return wikicode.filter_templates(matches=lambda node: node.name.strip() == template_name)
