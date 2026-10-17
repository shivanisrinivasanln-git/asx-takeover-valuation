// The report template. Every figure is read from valuation.json, so none is typed here.
// scripts/build_report.py copies this file and valuation.json into one folder and compiles it
// with the pinned Typst version; the disclaimer and the build date arrive as inputs.

#let data = json("valuation.json")
#let meta = data.meta

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

#let placeholder(what) = block(
  fill: luma(240),
  inset: 8pt,
  radius: 2pt,
  width: 100%,
)[Placeholder. #what]

#set document(title: "Shadow valuation of " + meta.target)
#set page(
  paper: "a4",
  margin: (x: 22mm, y: 24mm),
  footer: context [
    #set text(size: 8pt)
    #sys.inputs.disclaimer #h(1fr) #counter(page).display()
  ],
)
#set text(size: 10.5pt, lang: "en", region: "AU")
#set par(justify: false, leading: 0.65em)
#show heading: set block(above: 1.4em, below: 0.7em)
#show table.cell.where(y: 0): set text(weight: "bold")

#text(size: 22pt, weight: "bold")[Shadow valuation of #meta.target]

#v(0.3em)
Valuation date #meta.valuation_date. Built #sys.inputs.build_date. All values are A\$ per share unless a heading says otherwise.

= Method and result

#placeholder[The three methods and my range, with a source for each input.]

= Value per share by method

#table(
  columns: (1fr, auto, auto, auto),
  align: (left, right, right, right),
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { (bottom: 0.2pt + luma(200)) },
  inset: (x: 6pt, y: 5pt),
  table.header[Method][Low (A\$)][Preferred (A\$)][High (A\$)],
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

= Business operations value, A\$m

#table(
  columns: (1fr, auto, auto, auto),
  align: (left, right, right, right),
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { (bottom: 0.2pt + luma(200)) },
  inset: (x: 6pt, y: 5pt),
  table.header[Source][Low (A\$m)][Mid (A\$m)][High (A\$m)],
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

#placeholder[The gap bridge in words, and what I could not verify.]

#let bridge = data.gap_bridge

#table(
  columns: (1fr, auto, auto),
  align: (left, right, right),
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { (bottom: 0.2pt + luma(200)) },
  inset: (x: 6pt, y: 5pt),
  table.header[Step][Change (A\$)][Value after the step (A\$)],
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

= Limitations

#placeholder[What I could not verify.]
