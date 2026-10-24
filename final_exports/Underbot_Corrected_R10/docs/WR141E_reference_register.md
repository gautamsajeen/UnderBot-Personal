# WR141E M500 reference register — 2026-10-18

Independent research for the R10 correction. This register distinguishes published dimensions from visual estimates. None of the image-derived dimensions below is a measured hardware value or manufacturing tolerance.

## Primary sources

1. [Worx WR141E product page](https://eu.worx.com/en/robot-mower-landroid-s-robot-mower-for-lawns-up-to-400-m2-wr141e/). The current page title incorrectly says S400, but its SKU, technical table and supplied-product list identify WR141E / M500. Technical table: **558 mm depth, 404 mm width, 205 mm height; one front wheel; 9.1 kg with battery**. These are whole-product envelope dimensions, not chassis bounding-box dimensions or axle dimensions. The page also identifies keypad / four-digit LED interface. Do not use WR165E M500 Plus as a substitute.
2. [Worx original WR141E manual](https://cdn2.hubspot.net/hubfs/5237793/User%20Manual/Landroid%20M%202019/User_Manual_WR141E_EN.pdf), linked directly from that manufacturer page. Local PDF: `User_Manual_WR141E_EN.pdf`. Page 7 illustrates charge contacts, rain sensor, height adjustment, STOP, interface and rear opening battery hood. Page 36 specifies **8.5 kg machinery weight**, which differs from the current product page. It does not publish tyre diameter, track, wheelbase or mounting-hole coordinates. Page 24 uses a generic underside picture showing two front casters; this conflicts with the model-specific one-wheel specification and must not control WR141E caster count.
3. [Worx range comparison](https://eu.worx.com/en/landroid/landroid-models/). Explicit M500 WR141E row: one front wheel. Larger L-series rows have two.
4. Official photographs obtained from the manufacturer product-page asset links. `official_WR141E_view4.webp` is the top view; `official_WR141E_view5.webp` is front/left three-quarter; `official_WR141E_view6.webp` is rear/right three-quarter. Their URLs are recorded in `sources.json`. Existing earlier front/right views remain under `work/worx_refs/`.
5. [Positec spare catalogue](https://positec.ricambio.net/). Public page is accessible but drawings require catalogue login. Follow-up research retrieved the model-specific deck exploded drawing through ADEO, documented below. No dimensioned axle diagram was retrieved.

## Supplementary drawing

[Dimensioned WR141E drawing hosted by retailer Cardelli](https://ferramentacardelli.com/cdn/shop/products/wr141_dimensioni_1042x700.png?v=1696526525), local `wr141_dimensioni_retailer.png`. Labels agree with the primary whole-product envelope. Publisher/manufacturer authorship of the image is not independently confirmed. Orthographic-looking views vary slightly in scale; do not treat pixels as factory measurements. Used only to estimate proportions and cross-check photographed contours.

## Visual construction observations

The official photographs show a rounded orange nose and front side shell surrounding an irregular dark central deck; the rear battery hatch is black. The moulded shell slopes toward the nose, with distinct shoulders and panel seams. It is not a flat constant-height orange slab. Coarse staggered tyre lugs protrude beyond a dark three-web wheel face with a round hub cap. The front slotted guard occupies the robot's right half, rather than spanning the full width. The red charging assembly sits on the robot's right side. A large orange height dial lies beside it; STOP and LED/keypad are a separate cluster on the left. The STOP lies rearward of the display. A small rain-sensor insert is near the charge/dial assembly. Rear hatch and wheel arches are separate visible forms. These are visual inferences from sources 1/4, corroborated by the manual's labelled diagram.

ROS coordinates here mean +X forward, +Y robot-left, +Z up. Therefore the charge contacts/dial belong at **negative Y**, and STOP/display at positive Y. Photo4 has the nose pointing right on the image; lower side in that photo is robot-right.

## Provisional geometry estimates

These are coarse modelling targets, not exact specifications. Keep them marked `image_estimate` and expose them as parameters. A physical survey is required to replace them.

| Feature | Image-derived target | Basis / uncertainty |
|---|---:|---|
| Drive tyre outer diameter | about 200–205 mm | Rear wheel is essentially full mower height in side/front drawing; uncertainty roughly 10 mm. OEM value not found. |
| Drive tyre width | about 45–50 mm | Top/front drawing; rough estimate, about 5 mm uncertainty. |
| Drive-wheel center track | about 334 mm | Front-view center spacing / overall width; roughly 10 mm uncertainty. |
| Drive axle X | about −170 mm | Relative to centered 558 mm envelope; roughly 10 mm uncertainty. |
| Front caster rolling center X | about +170 to +175 mm | Side drawing; roughly 15 mm uncertainty; swivel trail remains unmeasured. |
| Front caster diameter | about 80 mm | Side drawing; roughly 10 mm uncertainty. |
| Height-dial center | X≈+65 mm, Y≈−90 mm | Top drawing and official photo; roughly 15 mm uncertainty. |
| Height-dial outer surround diameter | about 110–120 mm | Top drawing; rough decorative-envelope estimate. |
| STOP center | X≈−10 mm, Y≈+35 mm | Top drawing; roughly 15 mm uncertainty. |
| LED/display center | X≈+55 mm, Y≈+35 mm | Top drawing; roughly 15 mm uncertainty. |

Do not replace an uncertain measurement with a fabricated precise one. In particular, third-party 200/202/205/210 mm aftermarket wheel or spike dimensions do not establish the stock tyre diameter. No OEM torque, friction, inertia tensor, stripped chassis mass or payload rating was found.

## R09 deficiencies actually inspected

Inspected `outputs/Underbot_Final_R09/renders/Underbot_R09_hero.png` and source `outputs/underbot_description/config/geometry_manifest.json`.

- `wr141e_orange_hood` is a constant-height 65 mm prism with a 12-vertex polygon, flat top and rear orange deck. It misses the sloping, rounded shell and black rear hatch.
- Its mesh envelope is only 380 mm wide; R09 reaches 404 mm using wheel outsides. The real image references show a wider front shell and recessed rear wheel arrangement, so overall-envelope equality alone is insufficient.
- `front_grille` spans 290 mm symmetrically, with evenly spaced vertical bars. Real visible guard is asymmetric and follows the rounded right-front contour.
- Wheel diameter is 185 mm and track 354 mm, explicitly unmeasured R09 assumptions. Smooth annular tyres with shallow grooves and bright aluminium hub discs do not match coarse stock lugs / dark three-web faces.
- Height dial is only 40 mm diameter, next to an invented flat rectangular control board. Dial/charging contacts have positive Y, the wrong side for ROS orientation. STOP and display ordering/positions also need correction.
- Box-like side trim and lack of hatch, rain-sensor detail, shaped charge housings, stock wheel relief and rounded shell seams make it recognisable as a generic rover rather than WR141E.
- R09's clear rear service panel conflicts with the latest user instruction: all **four vertical sides** must be opaque black plastic. Only horizontal internal polycarbonate floor plates are transparent. Black aluminium frame surfaces should remain black, including exposed end faces if painted.

The previous thousands of geometry/format checks established consistency with an approximate source model. They did not establish manufacturer dimensional fidelity. The corrected delivery must explicitly separate confirmed dimensions, user-defined dimensions and unresolved component measurements.

## Follow-up: online stock-wheel dimensions

The user requested that required dimensions be obtained online. This follow-up supersedes the provisional wheel-diameter entries above where a part-specific published value was found.

| Item | Online evidence | Model use / confidence |
|---|---|---|
| Rear wheel identity | [WR141E deck exploded parts PDF, hosted by ADEO](https://media.adeo.com/media/5418924/media.pdf), item 65: part **50024699**, quantity 2 | Exact WR141E model-to-part mapping. Original parts-list content hosted by a retailer group. |
| Front wheel identity | Same parts PDF, item 51: assembly **50036897**, quantity 1 | Confirms the correct single caster assembly. |
| Rear diameter | [Clas Ohlson original 50024699 part listing](https://www.clasohlson.com/no/Hjul-Bakre-Worx-Landroid/p/51-2138): **205 mm** outer diameter, 16.7 mm internal bore | Published supplier specification, tied to exact OEM number. Use 205 mm instead of R09's 185 mm. |
| Rear diameter corroboration | [AgriEuro exact WR141E product page](https://www.agrieuro.co.uk/worx-landroid-wr141e-robot-lawn-mower-with-perimeter-wire-lithium-ion-battery-m500-p-22628.html): 205 mm rear wheels | Independent seller description of this mower, supports the original-part listing. |
| Front diameter / shaft | [Clas Ohlson 50036897](https://www.clasohlson.com/no/Hjul-fremre-Worx-Landroid-Landxcape/p/51-3393): **79 mm diameter**, **8 mm shaft**, expressly lists WR141E compatibility | Supplier specification; 79 mm nominal is better supported than a photo estimate. |
| Front diameter / width | [LetMeRepair Poland 50036897](https://sklep.letmerepair.pl/pl/p/WORX-Przednie-kolo-do-kosiarki-autonomicznej-50036897/803): **approximately 80 mm diameter, approximately 55 mm width**; explicitly fits WR141E | Supplier explicitly qualifies values as approximate. Preserve that qualification. |
| Rear width | Clas Ohlson lists package 205 × 205 × 40 mm, not tyre width. [OBI WA0952 listing](https://www.obi.ch/fr/accessoires-pour-tondeuses-a-gazon/worx-roues-crantees-wa0952-pour-robots-de-tonte-landroid-modeles-m/p/5501697) lists net 205 × 205 × 40 mm for the compatible weighted accessory | Stock-wheel width is **not established** by these sources. The accessory differs from the stock wheel. Packaging dimensions are not engineering measurements. |
| Track / axle spacing / caster trail | Targeted searches in English, German, French and part listings produced no dimensioned model-specific value | Remain explicitly image-derived estimates, not manufacturer specifications. |

Downloaded `WR141E_exploded_parts_Adeo.pdf` and rendered `WR141E_exploded_deck.png` show separate tyre wheel, circular counterweight, dark three-web outer roller guard and front caster. This independently explains the stock hub appearance and disproves R09's bright plain aluminium hub disc. Front-wheel width has weaker evidence than its diameter: the LetMeRepair approximately 55 mm statement has not been independently corroborated, and another seller's package thickness is inconsistent; do not call it a measured factory tolerance.

Aftermarket traction rings and replacement wheel designs were also searched. Their outer diameters are intentionally larger or their fit spans multiple generations, so they were not used to redefine stock dimensions. No online publication found in this search supports exact stock track, wheelbase, carrier trail, hidden mounting-hole positions, stripped chassis mass, inertia tensor or actuator limits. Online research can improve the model substantially but cannot honestly establish those unavailable values.

## R10 final model use — 24 October 2026

The manufacturer envelope and exact-part supplier wheel diameters were rechecked online on this date. The initial estimate table above is research history; the follow-up supplier values supersede its rear/front diameter estimates. The final model uses rear Ø205 × 40 mm, track334 mm, drive axleX−170 mm, casterØ79 ×55 mm, zero-swivel roll centreX+170 mm and trail20 mm. Only the diameters have exact-part published support; front width is supplier-approximate, and rear width/track/axle placement/trail remain estimates. The model's 40 mm rear width is not established by package dimensions.

The final tower has 200 ×200 mm floors, 204 ×204 mm cover bounds, 500 mm black aluminium posts, four opaque black vertical plastic covers and clear polycarbonate horizontal floors/camera shelf. Tower centreX−140 mm is a proposed installation location. Bare Kinect packaging, arm pivots, actual installed mass distribution, mounting holes and motor limits remain unmeasured. Local reference photographs and manual files named above were working references; this delivery includes their URLs and evidence notes, not copies of those third-party images.
