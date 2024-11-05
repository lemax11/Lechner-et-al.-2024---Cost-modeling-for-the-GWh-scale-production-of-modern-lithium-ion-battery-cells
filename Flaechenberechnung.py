# -*- coding: utf-8 -*-
"""
Created on Wed May 18 12:47:24 2022

@1st author: bendzuck
@2nd author: mahin
"""


def flaechenberechnung(flaeche_normalraum,flaeche_trockenraum,Gebaeude,Oekonomische_Parameter,flaeche_labor):

    #Paramter
    Zinssatz_kapitalmarkt = Oekonomische_Parameter["Wert"]["Capital cost"] #[%]
    
    nutzungsdauer_gebaeude = Gebaeude["Wert"]["Service life"] #[Jahre]
    
    
    produktionsflaeche = flaeche_normalraum + flaeche_trockenraum + flaeche_labor
    anteil_trockenraum_an_produktion = flaeche_trockenraum/produktionsflaeche
    anteil_laborraum_an_produktion = flaeche_labor/produktionsflaeche
    anteil_normalraum_an_produktion = flaeche_normalraum/produktionsflaeche

    
    #Produktionsfläche
    maschinenplatz_flaeche_prozent = Gebaeude["Wert"]["Factor machine space"] #[%]
    zwischenlager_flaeche_prozent = Gebaeude["Wert"]["Factor intermediate storage areas"] #[%]
    zusatz_flaeche_prozent = Gebaeude["Wert"]["Factor additional areas"] #[%]
    quadratmeter_preis_trockenraum = Gebaeude["Wert"]["Dry room building cost"] #[€/m²]
    quadratmeter_preis_labor = Gebaeude["Wert"]["Laboratory building cost"] #[€/m²]
    
    #Nutzfläche
    verwaltungs_flaeche_prozent = Gebaeude["Wert"]["Factor administrative areas"] #[%]
    lager_versand_flaeche_prozent = Gebaeude["Wert"]["Factor storage and shipping areas"] #[%]
    
    #Gebäudefläche
    neben_funktions_sozial_flaeche_prozent = Gebaeude["Wert"]["Factor ancillary, functional and social areas"] #[%]
    quadratmeter_preis_gebaeude = Gebaeude["Wert"]["Factory building cost"] #[€/m²]
    
    #Grunstücksffläche
    zusatzfaktor_grundstueck_prozent = Gebaeude["Wert"]["Factor undeveloped area"] #[%]
    quadratmeter_preis_grundstueck = Gebaeude["Wert"]["Property cost"] #[€/m²]
    
    #Berechnung Produktionsfläche
    maschinenplatz_flaeche = maschinenplatz_flaeche_prozent*produktionsflaeche/100
    zwischenlager_flaeche = zwischenlager_flaeche_prozent*produktionsflaeche/100
    zusatz_flaeche = zusatz_flaeche_prozent/100*produktionsflaeche
    
    
    #Berechnung Nutzfläche
    nutzflaeche =  produktionsflaeche/(1-(verwaltungs_flaeche_prozent+lager_versand_flaeche_prozent)/100)
    verwaltungs_flaeche = verwaltungs_flaeche_prozent*nutzflaeche/100
    lager_versand_flaeche = lager_versand_flaeche_prozent*nutzflaeche/100
    
    #Berechnung Gebäudefläche  
    gebaeudeflaeche = nutzflaeche/(1-neben_funktions_sozial_flaeche_prozent/100)
    neben_funktions_sozial_flaeche = neben_funktions_sozial_flaeche_prozent*gebaeudeflaeche/100
    
    #Berechnung Grundstücksfläche
    grundstuecksflaeche =  gebaeudeflaeche*(1+zusatzfaktor_grundstueck_prozent/100)
    unbebaute_flaeche = grundstuecksflaeche-gebaeudeflaeche
    
    
    
    
    investition_kosten_bau = [
        {
            "group": "Land costs",
            "value": round(grundstuecksflaeche*quadratmeter_preis_grundstueck)
        },
        {
            "group": "Factory costs",
            "value": round(gebaeudeflaeche*quadratmeter_preis_gebaeude)
        },
        {
            "group": "Dry room costs",
            "value": round(flaeche_trockenraum*quadratmeter_preis_trockenraum)
        },
        {
            "group": "Laboratory costs",
            "value": round(flaeche_labor*quadratmeter_preis_labor)
        }
        
                              ]

    anteil_trockenraum_an_produktion = flaeche_trockenraum/produktionsflaeche
    anteil_laborraum_an_produktion = flaeche_labor/produktionsflaeche
    anteil_normalraum_an_produktion = flaeche_normalraum/produktionsflaeche   
    anteil_anlagengrundflaeche_an_produktion = 1 - (maschinenplatz_flaeche_prozent + zwischenlager_flaeche_prozent + zusatz_flaeche_prozent)/100

    flaechen_verteilung = [
    
        {
            "name": "Outdoor areas",
            "children": [
                {
                    "name": "Outdoor areas",
                    "value": round(unbebaute_flaeche)
                }
            ]
        }, {
            "name": "Building areas",
            "children": [
                {
                    "name": "Ancillary, functional and social areas",
                    "value": round(neben_funktions_sozial_flaeche)
                },
                {
                    "name": "Storage and shipping areas",
                    "value": round(lager_versand_flaeche)
                },
                {
                    "name": "Administrative areas",
                    "value": round(verwaltungs_flaeche)
                }
            ]
        }, {
            "name": "Production areas",
            "children": [
                {
                    "name": "Additional areas in the dry room",
                    "value": round(zusatz_flaeche*anteil_trockenraum_an_produktion)
                },
                { "name": "Additional areas in the Laboratory",
                    "value": round(zusatz_flaeche*anteil_laborraum_an_produktion)
                
                },
                { "name": "Additional areas in the normal room",
                    "value": round(zusatz_flaeche*anteil_normalraum_an_produktion)
                
                },
                {
                    "name": "Intermediate storage areas in the dry room",
                    "value": round(zwischenlager_flaeche*anteil_trockenraum_an_produktion)
                },
                { "name": "Intermediate storage areas in the laboratory",
                    "value": round(zwischenlager_flaeche*anteil_laborraum_an_produktion)
                
                },
                { "name": "Intermediate storage areas in the normal room",
                    "value": round(zwischenlager_flaeche*anteil_normalraum_an_produktion)
                
                },
                  {
                    "name": "Machine areas in the dry room",
                    "value": round(maschinenplatz_flaeche*anteil_trockenraum_an_produktion)
                },
                { "name": "Machine areas in the laboratory",
                    "value": round(maschinenplatz_flaeche*anteil_laborraum_an_produktion)
                
                },
                { "name": "Machine areas in the normal room",
                    "value": round(maschinenplatz_flaeche*anteil_normalraum_an_produktion)
                
                },
                {
                    "name": "Plant floor areas for the dry room",
                    "value": round(flaeche_trockenraum*anteil_anlagengrundflaeche_an_produktion)
                },
                {
                    "name": "Plant floor areas for the normal room",
                    "value": round(flaeche_normalraum*anteil_anlagengrundflaeche_an_produktion)
                },
                {
                    "name": "Plant floor areas for the laboratory",
                    "value": round(flaeche_labor*anteil_anlagengrundflaeche_an_produktion)
                }
            ]
        }
    
    ]
    
    Fabrikflaeche = round(
        neben_funktions_sozial_flaeche+
        lager_versand_flaeche+
        verwaltungs_flaeche+
        flaeche_trockenraum+
        flaeche_normalraum+
        flaeche_labor
    )


    Fabrikflaeche_ohne_Produktion = round(Fabrikflaeche-produktionsflaeche)
    
    jaehrliche_flaechenkosten = quadratmeter_preis_gebaeude*Zinssatz_kapitalmarkt/100+quadratmeter_preis_gebaeude/nutzungsdauer_gebaeude
    
    return investition_kosten_bau, flaechen_verteilung, jaehrliche_flaechenkosten, Fabrikflaeche, Fabrikflaeche_ohne_Produktion, anteil_anlagengrundflaeche_an_produktion
    

#flaechenberechnung(flaeche_normalraum,flaeche_trockenraum)
