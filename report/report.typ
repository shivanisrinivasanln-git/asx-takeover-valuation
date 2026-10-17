// The report template. Every figure is read from valuation.json or limitations.json, so none is
// typed here; page numbers in the text are references, not figures. scripts/build_report.py
// copies this file and the two data files into one folder and compiles it with the pinned Typst
// version; the disclaimer and the build date arrive as inputs.

#let data = json("valuation.json")
#let limitations = json("limitations.json")
#let meta = data.meta
#let bridge = data.gap_bridge

#let val(key) = data.values.at(key).value

// The same rules as src/valuation/site_format.py: thousands separators, a true minus sign and
// no sign on a value that rounds to zero.
#let minus = "\u{2212}"

#let group-thousands(digits) = {
  let out = ""
  let count = digits.len()
  for (index, digit) in digits.clusters().enumerate() {
    if index > 0 and calc.rem(count - index, 3) == 0 { out += "," }
    out += digit
  }
  out
}

#let number(x, places: 2) = {
  let rounded = calc.round(x, digits: places)
  let parts = str(calc.abs(rounded)).split(".")
  let fraction = if parts.len() > 1 { parts.at(1) } else { "" }
  while fraction.len() < places { fraction += "0" }
  let text = group-thousands(parts.at(0))
  if places > 0 { text += "." + fraction }
  if rounded < 0 { minus + text } else { text }
}

#let signed(x, places: 2) = {
  let text = number(x, places: places)
  if text.starts-with(minus) or calc.round(x, digits: places) == 0 { text } else { "+" + text }
}

// The site's colours for ink, muted ink and the accent (site/static/tokens.css, light theme).
#let ink = rgb("#1c1f26")
#let muted = rgb("#575b64")
#let accent = rgb("#2148b8")
#let rule = rgb("#e3e1dc")

#set document(title: "Shadow valuation of " + meta.target)
#set page(
  paper: "a4",
  margin: (x: 22mm, top: 24mm, bottom: 26mm),
  footer: context [
    #set text(size: 7.5pt, fill: muted)
    #sys.inputs.disclaimer #h(1fr) #counter(page).display()
  ],
)
// The site's typeface, from the tracked font file in report/fonts; nothing else is used.
#set text(font: "Atkinson Hyperlegible Next", fallback: false, size: 10pt, fill: ink, lang: "en", region: "AU")
#set par(justify: false, leading: 0.7em, spacing: 1.1em)
#show heading: set text(weight: 600)
#show heading.where(level: 1): it => block(above: 1.8em, below: 0.8em)[
  #set text(size: 13pt)
  #it.body
]
#show heading.where(level: 2): it => block(above: 1.2em, below: 0.5em)[
  #set text(size: 10.5pt)
  #it.body
]
#show table: set text(number-width: "tabular", size: 9.5pt)
#show table.cell.where(y: 0): set text(weight: 600)

#let figures-table(columns, header, ..cells) = table(
  columns: columns,
  align: (x, y) => if x == 0 { left } else { right },
  stroke: (x, y) => if y == 0 { (bottom: 0.8pt + ink) } else { (bottom: 0.4pt + rule) },
  inset: (x: 6pt, y: 5pt),
  table.header(..header),
  ..cells,
)

#text(size: 20pt, weight: 600)[Shadow valuation of #meta.target]
#v(0.2em)
#text(fill: muted)[Valuation date #meta.valuation_date. Built #sys.inputs.build_date. Values are A\$ per share unless a heading says otherwise.]
#v(0.6em)
#line(length: 100%, stroke: 1.2pt + accent)

= Summary

My valuation range for #meta.target is A\$#number(val("combined_value_per_share_aud_low"))–#number(val("combined_value_per_share_aud_high")) a share, with a preferred value of A\$#number(val("preferred_value_per_share_aud")). CoStar Group's offer of A\$#number(val("offer_price_aud")) is inside my range and above my preferred value. Grant Samuel, the independent expert, valued Domain at A\$#number(val("expert_value_per_share_aud_low"))–#number(val("expert_value_per_share_aud_high")) a share.

I valued Domain at #meta.valuation_date, the expert's valuation date, from the scheme booklet, which holds the expert's report, and other public documents. Page numbers below are booklet pages. The website, the Excel model and this report are built from the same figures, and tests check that they agree.

= Method and result

I value Domain three ways. My preferred value weights the middle value of the discounted cash flow at #number(val("method_weight_dcf_pct"), places: 0)% and of each multiples method at #number(val("method_weight_trading_pct"), places: 0)%, and my range applies the same weights to the three low values and to the three high values. The expert gives no weights and says its range cannot be reduced to a weighting calculation (p. 135), so the weights are my judgement.

*Discounted cash flow.* I forecast free cash flow from the second half of FY25 to FY35 on the expert's scenario A inputs (pp. 141 to 142), discount it at #number(val("dcf_discount_rate_pct_high"), places: 1)% to #number(val("dcf_discount_rate_pct_low"), places: 1)%, the expert's adopted range (p. 140), and add a terminal value at #number(val("dcf_terminal_growth_pct"), places: 1)% growth (p. 142). The value is A\$#number(val("dcf_value_per_share_aud_low"))–#number(val("dcf_value_per_share_aud_high")) a share, and A\$#number(val("preferred_dcf_value_per_share_aud")) at a #number(val("dcf_discount_rate_pct_mid"), places: 1)% discount rate.

*Trading comparables.* I apply #number(val("trading_ebitda_multiple_x_low"), places: 1)x to #number(val("trading_ebitda_multiple_x_high"), places: 1)x, the forecast EBITDA multiples of SEEK and Rightmove, the two lowest of the expert's eight peers (p. 150), to FY26 adjusted EBITDA of A\$#number(val("trading_ebitda_earnings_aud_m"), places: 1)m (p. 153). Domain is the second portal in its market and its margin is well below REA Group's (p. 142), which is why I take the low end. Peer multiples come from minority share prices, so I add a control premium of #number(val("trading_ebitda_control_premium_pct"), places: 0)% at enterprise value level, within the expert's typical range (p. 158). The value is A\$#number(val("trading_ebitda_value_per_share_aud_low"))–#number(val("trading_ebitda_value_per_share_aud_high")) a share, and A\$#number(val("preferred_trading_value_per_share_aud")) at the midpoint.

*Precedent transactions.* I apply #number(val("precedent_ebitda_multiple_x_low"), places: 1)x to #number(val("precedent_ebitda_multiple_x_high"), places: 1)x, the deals with a forecast EBITDA multiple less the highest and the lowest (pp. 146 and 147), to the same earnings with no premium, because a takeover price already includes control. The value is A\$#number(val("precedent_ebitda_value_per_share_aud_low"))–#number(val("precedent_ebitda_value_per_share_aud_high")) a share, and A\$#number(val("preferred_precedent_value_per_share_aud")) at the midpoint.

== Value per share by method

#figures-table(
  (1fr, auto, auto, auto),
  ([Method], [Low (A\$)], [Preferred (A\$)], [High (A\$)]),
  ..for row in data.football_field {
    (
      row.label,
      number(val(row.low_key)),
      if row.preferred_key == none { "Not published" } else { number(val(row.preferred_key)) },
      number(val(row.high_key)),
    )
  },
)

Offer price A\$#number(val("offer_price_aud")). Undisturbed share price A\$#number(val("undisturbed_share_price_aud")).

== Business operations value, A\$m

#figures-table(
  (1fr, auto, auto, auto),
  ([Source], [Low (A\$m)], [Mid (A\$m)], [High (A\$m)]),
  [My discounted cash flow],
  number(val("dcf_business_operations_value_aud_m_low"), places: 1),
  number(val("dcf_business_operations_value_aud_m_mid"), places: 1),
  number(val("dcf_business_operations_value_aud_m_high"), places: 1),
  [Independent expert],
  number(val("expert_business_operations_value_aud_m_low"), places: 1),
  [],
  number(val("expert_business_operations_value_aud_m_high"), places: 1),
)

= Gap between the expert and me

Grant Samuel published a range and no preferred value, so the bridge starts at A\$#number(bridge.start_value_per_share_aud), the midpoint of its range, and ends at my preferred value of A\$#number(bridge.end_value_per_share_aud). Each step swaps one group of inputs from the expert's value to mine, in the order shown, and each change is the effect of that swap with the steps before it already made. Where I kept the expert's input the change is zero.

#figures-table(
  (1fr, auto, auto),
  ([Step], [Change (A\$)], [Value after the step (A\$)]),
  [#bridge.start_label],
  [],
  number(bridge.start_value_per_share_aud),
  [Reconstruction difference],
  signed(bridge.reconstruction_change_aud, places: 4),
  [],
  ..for step in bridge.steps {
    (
      [#step.label],
      signed(step.change_aud),
      number(step.cumulative_value_per_share_aud),
    )
  },
  [My preferred value],
  [],
  number(bridge.end_value_per_share_aud),
)

#for step in bridge.steps [
  == #step.label
  #step.explanation
]

= What I could not verify

#for item in limitations [
  - #item
]
