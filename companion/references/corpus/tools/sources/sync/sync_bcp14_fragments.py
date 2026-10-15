#!/usr/bin/env python3
"""BCP 14 (RFC 2119 + RFC 8174) → `sources.law` пакета `org/ietf/bcp14`.

ФАЙЛ-ВЫХОД ПОРОЖДАЕТСЯ. `corpus/laws/org/ietf/bcp14/sources.law` правится только
этим генератором; сверка без записи — ключ `--check`. Тексты фрагментов
вырезаются из закреплённых байтов, поэтому разойтись с публикацией не могут:
§194 отвергнет фрагмент, которого нет в байтах (LDC-E5202).

ДВА ДОКУМЕНТА В ОДНОМ ПАКЕТЕ, И ЭТО НЕ УДОБСТВО, А СОСТАВ СВОДА. «BCP 14» —
номер СВОДА лучших современных практик, за которым с мая 2017 года стоят два
самостоятельных RFC. Ни один из них не отменён: RFC 8174 несёт заголовок
`Updates: 2119`, а не `Obsoletes: 2119`, и в силе они одновременно.

ПОЧЕМУ ФРАГМЕНТ НЕ КОНЧАЕТСЯ АППАРАТОМ ИЗДАТЕЛЯ. Канонический RFC — плоский
текст, разбитый на страницы; между разделами регулярно стоит постраничный
аппарат («Bradner   Best Current Practice   [Page 1]», перевод формата U+000C,
колонтитул следующей страницы). Он ОСТАЁТСЯ в закреплённых байтах
(`corpus/tools/sources/fetch/fetch_bcp14_texts.py` объясняет, почему их нельзя
нормализовать) и честно лежит в непокрытом остатке байтовой меры; из ХВОСТА
фрагмента он снимается здесь — иначе покрытие текста притворилось бы покрытием
нормы (тот же довод, что у обрывов `cut` в шаблоне `pinning`).

СРЕЗ ПРИ ЭТОМ ОБРЫВАЕТСЯ ТОЛЬКО СЛЕДУЮЩИМ ЗАГОЛОВКОМ. Обрыв ПО аппарату,
стоявший здесь сначала, был безвреден на BCP 14 по совпадению — ни один раздел
RFC 2119 и RFC 8174 не продолжается после разрыва страницы, — и оказался
неверен на первом же протокольном RFC: раздел 3.3.3 RFC 7230 занимает три
страницы, и такой обрыв съедал из него четыре пункта из семи молча.

ABSTRACT RFC 2119 ЗАКРЕПЛЁН ОТДЕЛЬНЫМ ФРАГМЕНТОМ, хотя разделом не является и
в знаменатель учёта разделов не входит (локатор `abstract`, не `section/N`).
Причина не в полноте покрытия: RFC 8174 §2 заменяет ИМЕННО его текст
(«=== OLD === … === NEW ===»), и без адресуемого фрагмента эта замена была бы
неописуема — нечем было бы сослаться на то, что заменено.

    python3 corpus/tools/sources/sync/sync_bcp14_fragments.py           # записать
    python3 corpus/tools/sources/sync/sync_bcp14_fragments.py --check   # сверить
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[4]
PKG = ROOT / "corpus/laws/org/ietf/bcp14"
TARGET = PKG / "sources.law"

#: Момент получения закреплённых копий — константа, а не момент сборки
#: (DECISION-0005 п. 6). Совпадает с `fetch_bcp14_texts.py`.
RETRIEVED_AT = "2026-08-30T09:00:00Z"

#: Заголовок раздела RFC и то, что обрывает его срез. Обязано совпадать с
#: конвенцией `rfc_section` в `verify/ci/gates/sources/check_source_pinning.py`:
#: две меры §33.1 и генератор фрагментов режут ОДНО множество единиц.
HEAD = re.compile(r"^(\d+)\.[ \t]+\S", re.M)
STOP = re.compile(r"\n\d+\.[ \t]+\S", re.M)

#: Постраничный аппарат издателя в ХВОСТЕ единицы: колонтитул страницы
#: («Bradner  Best Current Practice  [Page 1]»), перевод формата и шапка
#: следующей страницы («RFC 2119  RFC Key Words  March 1997»).
#:
#: СНИМАЕТСЯ ТОЛЬКО ХВОСТ, И РАЗЛИЧИЕ НЕСУЩЕЕ. Аппарат, попавший ВНУТРЬ
#: раздела (раздел занял больше страницы), остаётся: фрагмент обязан быть
#: НЕПРЕРЫВНОЙ подстрокой публикации (LDC-E5202), и вырезать из него середину
#: нельзя. Обрывать же срез по первому колонтитулу — как здесь было сначала —
#: значит терять нормативный текст: на RFC 7230 §3.3.3 такой обрыв съедал
#: четыре пункта из семи при полностью зелёном §194.
TAIL_FURNITURE = re.compile(
    r"(?:\n[ \t]*|\n\f[ \t]*|\n[^\n]*\[Page \d+\][ \t]*|\n(?:RFC \d+|BCP \d+)[^\n]*)+\Z")


class Document(NamedTuple):
    """Один RFC свода: символы source-модели и ожидаемый состав разделов."""

    slug: str                      # каталог под sources/
    number: str                    # номер RFC
    source: str                    # символ source §27
    edition: str                   # символ edition §27.2
    publication: str               # символ publication §27.3
    prefix: str                    # префикс имён фрагментов
    digest: str                    # sha256 закреплённых байтов
    sections: tuple[str, ...]      # ожидаемые номера разделов
    adopted: str                   # дата принятия (см. NOTE_ADOPTED)
    title: str
    author: str
    #: Разделы и их однострочные описания — комментарий над фрагментом.
    captions: dict[str, str]


RFC2119 = Document(
    slug="rfc2119", number="2119",
    source="RFC2119", edition="RFC2119_EN", publication="RFC2119_EN_TEXT",
    prefix="RFC2119",
    digest="3c2ceb7bfc84cd34720f4a5271338ab9d8280d34bdd1eb250c64306202f2ed8b",
    sections=("1", "2", "3", "4", "5", "6", "7", "8", "9"),
    adopted="1997-03-01",
    title="Key words for use in RFCs to Indicate Requirement Levels",
    author="S. Bradner",
    captions={
        "1": "MUST / REQUIRED / SHALL — абсолютное требование спецификации",
        "2": "MUST NOT / SHALL NOT — абсолютный запрет спецификации",
        "3": "SHOULD / RECOMMENDED — отступление при веской причине и взвешенных последствиях",
        "4": "SHOULD NOT / NOT RECOMMENDED — зеркало раздела 3 для воздержания",
        "5": "MAY / OPTIONAL — подлинно факультативно; и ДВА собственных MUST об интероперабельности",
        "6": "Норма о нормотворчестве: императивы MUST применять только там, где это нужно для интероперации или ограничения вредоносного поведения",
        "7": "Security Considerations: последствия неисполнения бывают неочевидны, авторам следует их раскрывать",
        "8": "Acknowledgments — граница, объявлена в articles.json",
        "9": "Author's Address — граница, объявлена в articles.json",
    },
)

RFC8174 = Document(
    slug="rfc8174", number="8174",
    source="RFC8174", edition="RFC8174_EN", publication="RFC8174_EN_TEXT",
    prefix="RFC8174",
    digest="5ca0e2f90be0bc5928ee465f76518fee316dfa775aed885658a29a419cc293b7",
    sections=("1", "2", "3", "4", "5"),
    adopted="2017-05-01",
    title="Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words",
    author="B. Leiba",
    captions={
        "1": "Introduction: RFC 2119 сказал «are often capitalized», и это породило неясность",
        "2": "Замена текста RFC 2119: специальное значение — только у ЗАГЛАВНЫХ форм",
        "3": "IANA Considerations — граница, объявлена в articles.json",
        "4": "Security Considerations — граница, объявлена в articles.json",
        "5": "Normative References — граница, объявлена в articles.json",
    },
)

DOCUMENTS = (RFC2119, RFC8174)

#: Abstract RFC 2119 — не раздел (локатор `abstract`), но адресуемый фрагмент:
#: именно его текст заменяет RFC 8174 §2. Границы среза объявлены дословно, а
#: не угаданы по отступам.
ABSTRACT_HEAD = "Abstract\n"
ABSTRACT_TAIL = "   level of the document in which they are used.\n"


def sections(document: str) -> list[tuple[str, str]]:
    """(номер, срез раздела) — от заголовка до следующего либо до колонтитула."""
    heads = list(HEAD.finditer(document))
    out: list[tuple[str, str]] = []
    for index, head in enumerate(heads):
        end = heads[index + 1].start() if index + 1 < len(heads) else len(document)
        tail = document[head.end():end]
        stop = STOP.search(tail)
        text = document[head.start(): head.end() + (stop.start() if stop else len(tail))]
        out.append((head.group(1), TAIL_FURNITURE.sub("", text).rstrip("\n")))
    return out


def abstract(document: str) -> str:
    """Срез Abstract: от объявленного начала до объявленного конца включительно."""
    start = document.find(ABSTRACT_HEAD)
    if start < 0:
        raise SystemExit("rfc2119: начало Abstract не найдено")
    end = document.find(ABSTRACT_TAIL, start)
    if end < 0:
        raise SystemExit("rfc2119: конец Abstract не найден")
    return document[start:end + len(ABSTRACT_TAIL)].rstrip("\n")


def fragment(ident: str, kind: str, locator: str, text: str, caption: str) -> list[str]:
    if '"""' in text:
        raise SystemExit(f"{ident}: в тексте фрагмента есть тройная кавычка")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return [f"// {caption}",
            f"fragment {ident} in {{edition}} {{{{",
            f"    kind {kind};",
            f'    locator "{locator}";',
            f'    text en official """{text}""";',
            f'    content_hash "sha256:{digest}";',
            "}}", ""]


HEADER = '''// Source-модель BCP 14: закреплённые байты обоих RFC свода и фрагменты
// всех их разделов.
//
// ФАЙЛ ПОРОЖДАЕТСЯ. Правится только генератором —
// `corpus/tools/sources/sync/sync_bcp14_fragments.py`; сверка без записи — его
// же ключом `--check`. Тексты вырезаются из `sources/rfc2119/en.txt` и
// `sources/rfc8174/en.txt`, поэтому разойтись с публикацией они не могут.
//
// ПРОВЕНАНС ЗДЕСЬ ЛУЧШЕ, ЧЕМ У ЛЮБОГО ДРУГОГО ПАКЕТА КОРПУСА, и это следствие
// устройства серии, а не нашего усердия. Канонический формат RFC — плоский
// US-ASCII текст, и `https://www.rfc-editor.org/rfc/rfc2119.txt` отдаёт САМУ
// публикацию, а не её отрисовку: закрепляются байты издателя без единого
// преобразования. Поэтому здесь стоит `PINNED_OFFICIAL_BYTES`, а не
// `PINNED_UNOFFICIAL_COPY`, каким закреплены Конвенция о геноциде, ДНЯО и
// Римский статут, — и это утверждение проверяемо: sha256 обоих документов
// закреплён в `corpus/tools/sources/fetch/fetch_bcp14_texts.py`, и `--check`
// отказывает громко, если издатель однажды отдаст другой файл под тем же URL.
//
// ОПУБЛИКОВАННЫЙ RFC НЕ РЕДАКТИРУЕТСЯ НИКОГДА. Ошибки ведутся отдельным
// журналом errata; исправленный текст выходит НОВЫМ номером с заголовком
// `Obsoletes:`. Это ровно инвариант 1 настоящего репозитория (`release/` не
// правится, расхождение со `spec/` и есть накопленный журнал errata) — только
// у IETF он старше на тридцать лет. Следствие для закрепления: ревизия
// документа не нужна вовсе, достаточно номера.
//
// ПОЧЕМУ У ПАКЕТА ДВА `source`, А НЕ ДВЕ РЕДАКЦИИ ОДНОГО. RFC 8174 несёт
// заголовок `Updates: 2119`, а не `Obsoletes: 2119`: он ИЗМЕНЯЕТ прочтение
// RFC 2119, но не заменяет его, и оба документа входят в свод одновременно.
// Это два самостоятельных акта со своей нумерацией разделов, своим автором и
// своей датой, а не два состояния одного текста.
//
// ПОЧЕМУ ЗДЕСЬ НЕТ `revision`. Соблазн записать `revision { previous
// RFC2119_EN; next …; relation amends; }` велик: RFC 8174 §2 даёт дословную
// замену («=== OLD === … === NEW ===»), то есть является амендментом в самом
// строгом смысле. Но `revision` §31 связывает две РЕДАКЦИИ одного документа, а
// сводной редакции RFC 2119 с учтённой правкой НЕ СУЩЕСТВУЕТ и существовать не
// может: опубликованный RFC не переиздаётся. Объявить `next` было бы
// объявлением документа, которого нет. Связь выражена тем, что издатель для
// неё и завёл, — ссылкой §28 (`RFC8174_UPDATES_RFC2119`), отвечающей заголовку
// `Updates:`. Это и есть тот случай, когда «неизменяемость текста» перестаёт
// быть красивыми словами и становится ограничением модели.
//
// `retrieved_at` — константа, а не момент сборки (DECISION-0005 п. 6).
//
// ДАТА ПРИНЯТИЯ — ПЕРВОЕ ЧИСЛО НАЗВАННОГО МЕСЯЦА, И ЭТО ОБЪЯВЛЕННОЕ
// СОГЛАШЕНИЕ, А НЕ НАЙДЕННЫЙ ФАКТ. RFC датируется с точностью до месяца:
// шапка RFC 2119 несёт «March 1997», шапка RFC 8174 — «May 2017», дня в
// публикации нет вовсе. Машине редакций §31/D1 и окнам норм §140 нужна дата,
// и взята самая ранняя, совместимая с источником, — первое число месяца.
// Ни один сценарий пакета на выборе дня внутри месяца не держится: ближайшая
// проверка границы — пара BCP14-20/21 на СУТКАХ по обе стороны первого
// числа марта 1997 года.
'''


def build() -> str:
    out: list[str] = [HEADER]
    out.append('language "law.core" version "0.2";')
    out.append('package ietf.bcp14 version "0.1.0";')
    out.append('namespace "urn:ietf:clir:bcp14";')
    out.append("")

    for doc in DOCUMENTS:
        path = PKG / "sources" / doc.slug / "en.txt"
        payload = path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if digest != doc.digest:
            raise SystemExit(
                f"rfc{doc.number}: закреплённые байты дают sha256:{digest}, "
                f"а объявлено sha256:{doc.digest} — источник подменён")
        text = payload.decode("utf-8")

        found = sections(text)
        numbers = tuple(number for number, _ in found)
        if numbers != doc.sections:
            raise SystemExit(
                f"rfc{doc.number}: разделы {numbers}, объявлено {doc.sections} — "
                "разметка источника сдвинулась")

        out.append(f"// ═══ RFC {doc.number} ═══════════════════════════════"
                   "══════════════════════════")
        out.append("")
        out.append(f"source {doc.source} {{")
        out.append("    kind best_current_practice;")
        out.append("    jurisdiction IETF;")
        out.append("    authority IETF;")
        out.append(f'    number "RFC {doc.number}, BCP 14";')
        out.append(f'    label en official "{doc.title}";')
        out.append("}")
        out.append("")
        out.append(f"edition {doc.edition} of {doc.source} {{")
        out.append(f'    label en official "RFC {doc.number} ({doc.author})";')
        out.append("    language en;")
        out.append("    officiality official;")
        out.append(f"    adopted @{doc.adopted};")
        out.append(f"    in_force [@{doc.adopted}, infinity);")
        out.append("    materialization_status PINNED_OFFICIAL_BYTES;")
        out.append("}")
        out.append("")
        out.append(f"publication {doc.publication} of {doc.edition} {{")
        out.append('    media_type "text/plain; charset=us-ascii";')
        out.append(f'    uri "https://www.rfc-editor.org/rfc/rfc{doc.number}.txt";')
        out.append(f"    retrieved_at @{RETRIEVED_AT};")
        out.append(f'    content_hash "sha256:{doc.digest}";')
        out.append(f'    local_path "sources/{doc.slug}/en.txt";')
        out.append("}")
        out.append("")

        if doc is RFC2119:
            body = abstract(text)
            if body not in text:
                raise SystemExit("rfc2119: срез Abstract не подстрока публикации")
            out += [line.format(edition=doc.edition)
                    for line in fragment(
                        f"{doc.prefix}_ABSTRACT", "section", "abstract", body,
                        "Abstract — НЕ раздел (в знаменатель учёта не входит); "
                        "закреплён потому, что RFC 8174 §2 заменяет именно его текст")]

        for number, body in found:
            if body not in text:
                raise SystemExit(f"rfc{doc.number}: срез раздела {number} "
                                 "не является подстрокой публикации")
            out += [line.format(edition=doc.edition)
                    for line in fragment(f"{doc.prefix}_S{number}", "section",
                                         f"section/{number}", body,
                                         f"Раздел {number}. {doc.captions[number]}")]

    out.append("// Заголовок `Updates: 2119` в шапке RFC 8174 — машиночитаемое")
    out.append("// объявление самого издателя о том, что этот документ меняет")
    out.append("// прочтение того. Локатор указывает на Abstract: именно его")
    out.append("// текст заменён разделом 2 RFC 8174. См. шапку файла о том,")
    out.append("// почему связь записана ссылкой §28, а не `revision` §31.")
    out.append("reference RFC8174_UPDATES_RFC2119 {")
    out.append(f"    source {RFC2119.source};")
    out.append('    locator "abstract";')
    out.append("    // §30.2 требует момент разрешения ссылки; в срезе 0.1")
    out.append("    // допустимо единственное значение — `legal_time`.")
    out.append("    resolve_at legal_time;")
    out.append('    label en official "Updates: 2119 (RFC 8174, May 2017)";')
    out.append("}")
    out.append("")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="сверить порождаемое с закоммиченным, ничего не писать")
    args = parser.parse_args()

    rendered = build()
    if args.check:
        have = TARGET.read_text(encoding="utf-8") if TARGET.is_file() else ""
        if have == rendered:
            print(f"sync_bcp14_fragments: ✓ {TARGET.relative_to(ROOT)}")
            return 0
        print(f"sync_bcp14_fragments: ✗ {TARGET.relative_to(ROOT)} разошёлся "
              "с генератором — перегенерировать")
        return 1
    TARGET.write_text(rendered, encoding="utf-8")
    print(f"sync_bcp14_fragments: записан {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
