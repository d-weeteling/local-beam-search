# local-beam-search

Een algoritme voor het oplossen van sudoku puzzels
---

## Omschrijving

Met deze code kunnen sudoku's worden opgelost, zowel 9x9 als 16x16 als 25x25 (<=langzaam).

De code betreft een lokaal zoek algoritme, '(Local) Beam Search' waarbij ik de beam size
dynamisch van formaat laat veranderen (eigen innovatie): wanneer de beam te lang geen betere states
ontdekt, wordt de beam wijder. De beam zoekt zo in een groter gebied, wat de kans vergroot op het
vinden van een betere state. Omdat er meer states doorzocht worden, is dit echter langzamer.
Wanneer er weer een verbetering optreed, wordt de beam weer een maatje kleiner, en draait het
algoritme weer sneller. Dit bleek aanzienlijk beter te werken dan klassieke, statische beam search.

## Nota Bene

- NB! - De code rekent op Python 2 (i.t.t. Python 3)
- NB! - De code is een prototype met weinig commentaar, maar werkt verder perfect
- NB! - Hoe te gebruiken: $ python LocalBeamSearch_v4.py
- NB! - Meer info over het geïmplementeerde algoritme: http://en.wikipedia.org/wiki/Beam_search



