"""The site check reads script files as text and rejects anything that builds code from text,
makes a request, keeps data in the browser or writes markup (task P5-06)."""

from pathlib import Path

import pytest

from valuation.site_build import DISCLAIMER
from valuation.site_check import script_problems, site_problems

GOOD_SCRIPT = """(function () {
  "use strict";
  // A comment may mention eval, fetch and innerHTML: it is not code.
  var link = document.querySelector("a.source-mark");
  var box = document.getElementById("source-popover");
  box.hidden = false;
  box.style.top = "10px";
  link.setAttribute("aria-expanded", "true");
  link.addEventListener("click", function (event) {
    event.preventDefault();
  });
})();
"""


def test_a_script_that_only_changes_the_page_it_is_on_passes() -> None:
    assert script_problems(GOOD_SCRIPT) == []


def test_a_banned_word_in_a_comment_or_a_string_is_not_a_problem() -> None:
    script = (
        'var label = "fetch the figure";\n/* eval is not called here */\nvar x = 1; // innerHTML\n'
    )
    assert script_problems(script) == []


@pytest.mark.parametrize(
    ("code", "message"),
    [
        ('eval("1");', "uses eval"),
        ('var f = new Function("return 1");', "uses Function"),
        ('setTimeout("x()", 1);', "uses setTimeout"),
        ("setInterval(go, 1);", "uses setInterval"),
        ('fetch("data.json");', "uses fetch"),
        ("var r = new XMLHttpRequest();", "uses XMLHttpRequest"),
        ("navigator.sendBeacon(url);", "uses sendBeacon"),
        ('import("x.js");', "uses import"),
        ('el.innerHTML = "x";', "uses innerHTML"),
        ('el.outerHTML = "x";', "uses outerHTML"),
        ('el.insertAdjacentHTML("beforeend", "x");', "uses insertAdjacentHTML"),
        ('document.write("x");', "calls write"),
        ('window.open("a");', "calls open"),
        ("var v = localStorage.getItem(k);", "uses localStorage"),
        ("var v = sessionStorage.length;", "uses sessionStorage"),
        ("var v = document.cookie;", "uses cookie"),
        ('location.href = "x";', "uses location"),
        ("el.style.cssText = x;", "uses cssText"),
        ("var c = [].constructor.constructor(x);", "uses constructor"),
        ('window["ev" + "al"](x);', "reads window by a computed name"),
        ('this["a" + "b"]();', "reads this by a computed name"),
        ('var s = document.createElement("script");', 'uses the string "script"'),
        ('var s = document.createElement("iframe");', 'uses the string "iframe"'),
        ('el.setAttribute("style", "color: red");', 'uses the string "style"'),
        ('el.setAttribute("onclick", "go()");', 'uses the string "onclick"'),
        ("setImmediate(go);", "uses setImmediate"),
        ('importScripts("a.js");', "uses importScripts"),
        ('var s = new WebSocket("a");', "uses WebSocket"),
        ('var s = new EventSource("a");', "uses EventSource"),
        ('var w = new Worker("a.js");', "uses Worker"),
        ('var w = new SharedWorker("a.js");', "uses SharedWorker"),
        ("var w = navigator.serviceWorker;", "uses serviceWorker"),
        ("var d = indexedDB;", "uses indexedDB"),
        ("el.srcdoc = x;", "uses srcdoc"),
        ("target.postMessage(x);", "uses postMessage"),
        ("var g = globalThis;", "uses globalThis"),
        ("document.writeln(x);", "calls writeln"),
        ('self["a" + "b"]();', "reads self by a computed name"),
        ('var s = document.createElement("object");', 'uses the string "object"'),
        ('var s = document.createElement("embed");', 'uses the string "embed"'),
        ('var s = document.createElement("base");', 'uses the string "base"'),
        ('var s = document.createElement("link");', 'uses the string "link"'),
        ('var address = "data:text/plain,x";', "string with markup or an address"),
        ('var markup = "a > b";', "string with markup or an address"),
        ('var address = "//example.com";', "string with markup or an address"),
        ('var markup = "<img src=x>";', "string with markup or an address"),
        ('var address = "https://example.com/";', "string with markup or an address"),
        ('var address = "javascript:go()";', "string with markup or an address"),
        ("var pieces = text.split(/\\s/);", "a backslash"),
        ("var text = `a ${b}`;", "a template literal"),
        (f'var minus = "{chr(0x2212)}";', "a character outside ASCII"),
        ('var open = "abc', "unfinished string or comment"),
        ("/* never closed", "unfinished string or comment"),
    ],
)
def test_a_planted_problem_in_a_script_is_reported(code: str, message: str) -> None:
    problems = script_problems(f"var ok = 1;\n{code}\n")
    assert any(message in problem for problem in problems), problems


def test_a_problem_names_its_line() -> None:
    problems = script_problems('var a = 1;\nvar b = 2;\neval("x");\n')
    assert problems == ["line 3: script uses eval"]


def test_a_script_file_in_the_built_site_is_scanned_and_named(tmp_path: Path) -> None:
    (tmp_path / "static").mkdir()
    (tmp_path / "static" / "sources.js").write_text('eval("1");\n', encoding="utf-8")
    problems = site_problems(tmp_path, DISCLAIMER)
    assert "static/sources.js: line 1: script uses eval" in [
        problem.replace("\\", "/") for problem in problems
    ]
