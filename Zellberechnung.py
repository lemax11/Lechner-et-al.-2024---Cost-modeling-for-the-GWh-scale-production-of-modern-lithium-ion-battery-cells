# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 12:12:40 2022

@author: bendzuck
"""
import pandas as pd
import json
import math


#____________________________________
# die Eingangsparameter
# 1. Zellchemie [df]
# 2. Materialinfos [df]
# 3. Zellmaße [df]
# 4. Name Zellformat &  Zelltyp [JSON Object -> String]
# 5. Gesamtladung einer Zelle [float] (nur Pouchzelle) -> muss aus dem Frontend in eigenen redux state
# 6. Größe Gigafabrik in GWh/Jahr [float] -> muss aus dem Frontend in eigenen redux state, kann sich mit Gesamtladung teilen
# -> Hülle fehlt noch gesamt    

#Zellchemie = '[{"id":1,"Beschreibung":"NCM 622","Kategorie":"Aktivmaterial Kathode","Wert":97.0,"Einheit":"%"},{"id":2,"Beschreibung":"Graphit","Kategorie":"Aktivmaterial Anode","Wert":96.5,"Einheit":"%"},{"id":3,"Beschreibung":"Kupferfolie 10 \u00b5m","Kategorie":"Kollektorfolie Anode","Wert":null,"Einheit":"%"},{"id":4,"Beschreibung":"Aluminiumfolie 8 \u00b5m","Kategorie":"Kollektorfolie Kathode","Wert":null,"Einheit":"%"},{"id":6,"Beschreibung":"Wasser","Kategorie":"L\u00f6semittel Anode","Wert":3.0,"Einheit":"%"},{"id":10,"Beschreibung":"Zellspannung","Kategorie":"Allgemeine Parameter","Wert":3.7,"Einheit":"V"},{"id":11,"Beschreibung":"Irreversibler Formierungsverlust","Kategorie":"Allgemeine Parameter","Wert":10.0,"Einheit":"%"},{"id":12,"Beschreibung":"Zieldichte Beschichtung Kathode","Kategorie":"Elektrodenparameter Kathode","Wert":3.0,"Einheit":"g\/cm\u00b3"},{"id":13,"Beschreibung":"Beschichtungsporosit\u00e4t Kathode","Kategorie":"Elektrodenparameter Kathode","Wert":25.0,"Einheit":"%"},{"id":14,"Beschreibung":"Fl\u00e4chenspezifische Kapazit\u00e4t Kathode","Kategorie":"Elektrodenparameter Kathode","Wert":4.0,"Einheit":"mAh\/cm\u00b2"},{"id":15,"Beschreibung":"Feststoffgehalt Kathode","Kategorie":"Elektrodenparameter Kathode","Wert":60.0,"Einheit":"%"},{"id":16,"Beschreibung":"Zieldichte Beschichtung Anode","Kategorie":"Elektrodenparameter Anode","Wert":1.6,"Einheit":"g\/cm\u00b3"},{"id":17,"Beschreibung":"Beschichtungsporosit\u00e4t Anode","Kategorie":"Elektrodenparameter Anode","Wert":34.0,"Einheit":"%"},{"id":18,"Beschreibung":"Fl\u00e4chenspezifische Kapazit\u00e4t Anode","Kategorie":"Elektrodenparameter Anode","Wert":3.2,"Einheit":"mAh\/cm\u00b2"},{"id":19,"Beschreibung":"Feststoffgehalt Anode","Kategorie":"Elektrodenparameter Anode","Wert":60.0,"Einheit":"%"},{"id":20,"Beschreibung":"Kalkulierter Anoden\u00fcberschuss","Kategorie":"Elektrodenparameter Anode","Wert":10.0,"Einheit":"%"},{"id":21,"Beschreibung":"NMP","Kategorie":"L\u00f6semittel Kathode","Wert":63.4,"Einheit":"%"},{"id":22,"Beschreibung":"ProZell Separator","Kategorie":"Separator","Wert":null,"Einheit":"%"},{"id":23,"Beschreibung":"K-Leitru\u00df 1","Kategorie":"Additive Kathode","Wert":3.0,"Einheit":"%"},{"id":24,"Beschreibung":"K-Leitru\u00df 2","Kategorie":"Additive Kathode","Wert":0.0,"Einheit":"%"},{"id":25,"Beschreibung":"K-Additiv","Kategorie":"Additive Kathode","Wert":1.0,"Einheit":"%"},{"id":26,"Beschreibung":"K-Binder 1","Kategorie":"Additive Kathode","Wert":3.0,"Einheit":"%"},{"id":27,"Beschreibung":"K-Binder 2","Kategorie":"Additive Kathode","Wert":0.0,"Einheit":"%"},{"id":28,"Beschreibung":"A-Leitru\u00df 1","Kategorie":"Additive Anode","Wert":1.0,"Einheit":"%"},{"id":29,"Beschreibung":"A-Leitru\u00df 2","Kategorie":"Additive Anode","Wert":0.0,"Einheit":"%"},{"id":31,"Beschreibung":"A-Binder 1","Kategorie":"Additive Anode","Wert":1.0,"Einheit":"%"},{"id":32,"Beschreibung":"A-Binder 2","Kategorie":"Additive Anode","Wert":1.5,"Einheit":"%"},{"id":33,"Beschreibung":"1M LiPF6 (EC: EMC 3:7 wt%) + 2 wt% VC","Kategorie":"Elektrolyt","Wert":null,"Einheit":"%"}]'
#Materialinfos = '[{"NCM 622":[{"id":3,"Beschreibung":"spezifische Kapazität","Wert":160,"Einheit":"mAh/g"},{"id":4,"Beschreibung":"Dichte","Wert":0.476,"Einheit":"g/cm³"},{"id":5,"Beschreibung":"Preis","Wert":25.75,"Einheit":"€/kg"}]},{"Graphit":[{"id":1,"Beschreibung":"spezifische Kapazität","Wert":330,"Einheit":"mAh/g"},{"id":2,"Beschreibung":"Dichte","Wert":2.25,"Einheit":"g/cm³"},{"id":3,"Beschreibung":"Preis","Wert":7.46,"Einheit":"€/kg"}]},{"Kupferfolie 10 µm":[{"id":1,"Beschreibung":"Dicke","Wert":10,"Einheit":"µm"},{"id":2,"Beschreibung":"Dichte","Wert":8.96,"Einheit":"g/cm³"},{"id":3,"Beschreibung":"Breite","Wert":600,"Einheit":"mm"},{"id":4,"Beschreibung":"Preis","Wert":0.44,"Einheit":"€/m"}]},{"Aluminiumfolie 8 µm":[{"id":1,"Beschreibung":"Dicke","Wert":8,"Einheit":"µm"},{"id":2,"Beschreibung":"Dichte","Wert":2.7,"Einheit":"g/cm³"},{"id":3,"Beschreibung":"Breite","Wert":600,"Einheit":"mm"},{"id":4,"Beschreibung":"Preis","Wert":0.2,"Einheit":"€/m"}]},{"Wasser":[{"id":1,"Beschreibung":"Dichte","Wert":1,"Einheit":"g/cm³"},{"id":2,"Beschreibung":"Preis","Wert":0.01,"Einheit":"€/kg"}]},{"NMP":[{"id":1,"Beschreibung":"Dichte","Wert":1.2,"Einheit":"g/cm³"},{"id":2,"Beschreibung":"Preis","Wert":2.39,"Einheit":"€/kg"}]},{"ProZell Separator":[{"id":1,"Beschreibung":"Dicke","Wert":20,"Einheit":"µm"},{"id":2,"Beschreibung":"Dichte","Wert":10,"Einheit":"g/cm³"},{"id":3,"Beschreibung":"Porosität","Wert":40,"Einheit":"%"},{"id":4,"Beschreibung":"Breite","Wert":600,"Einheit":"mm"},{"id":5,"Beschreibung":"Preis","Wert":0.5,"Einheit":"€/m"}]},{"K-Leitruß 1":[{"id":1,"Beschreibung":"Dichte","Wert":2.25,"Einheit":"g/cm³"},{"id":2,"Beschreibung":"Preis","Wert":5.07,"Einheit":"€/kg"}]},{"K-Leitruß 2":[{"id":1,"Beschreibung":"Dichte","Wert":1,"Einheit":"g/cm³"},{"id":2,"Beschreibung":"Preis","Wert":5.07,"Einheit":"€/kg"}]},{"K-Additiv":[{"id":1,"Beschreibung":"Dichte","Wert":2.25,"Einheit":"g/cm³"},{"id":2,"Beschreibung":"Preis","Wert":10,"Einheit":"€/kg"}]},{"K-Binder 1":[{"id":1,"Beschreibung":"Dichte","Wert":1.3,"Einheit":"g/cm³"},{"id":2,"Beschreibung":"Preis","Wert":18,"Einheit":"€/kg"}]},{"K-Binder 2":[{"id":1,"Beschreibung":"Dichte","Wert":1.3,"Einheit":"g/cm³"},{"id":2,"Beschreibung":"Preis","Wert":18,"Einheit":"€/kg"}]},{"A-Leitruß 1":[{"id":1,"Beschreibung":"Dichte","Wert":2.25,"Einheit":"g/cm³"},{"id":2,"Beschreibung":"Preis","Wert":5.07,"Einheit":"€/kg"}]},{"A-Leitruß 2":[{"id":1,"Beschreibung":"Dichte","Wert":1,"Einheit":"g/cm³"},{"id":2,"Beschreibung":"Preis","Wert":5.07,"Einheit":"€/kg"}]},{"A-Binder 1":[{"id":1,"Beschreibung":"Dichte","Wert":1,"Einheit":"g/cm³"},{"id":2,"Beschreibung":"Preis","Wert":1.5,"Einheit":"€/kg"}]},{"A-Binder 2":[{"id":1,"Beschreibung":"Dichte","Wert":1,"Einheit":"g/cm³"},{"id":2,"Beschreibung":"Preis","Wert":1.5,"Einheit":"€/kg"}]},{"1M LiPF6 (EC: EMC 3:7 wt%) + 2 wt% VC":[{"id":1,"Beschreibung":"Dichte","Wert":1.3,"Einheit":"g/cm³"},{"id":2,"Beschreibung":"Preis","Wert":7.44,"Einheit":"€/kg"}]}]'
#Zellformat = '[{"id":1,"Beschreibung":"Breite Anode","Wert":null,"Einheit":"mm"},{"id":2,"Beschreibung":"L\u00e4nge Anode","Wert":null,"Einheit":"mm"},{"id":3,"Beschreibung":"Breite Zellf\u00e4hnchen Anode","Wert":22.0,"Einheit":"mm"},{"id":4,"Beschreibung":"L\u00e4nge Zellf\u00e4hnchen Anode","Wert":30.0,"Einheit":"mm"},{"id":5,"Beschreibung":"Breite Kathode","Wert":null,"Einheit":"mm"},{"id":6,"Beschreibung":"L\u00e4nge Kathode","Wert":null,"Einheit":"mm"},{"id":7,"Beschreibung":"Breite Zellf\u00e4hnchen Kathode","Wert":22.0,"Einheit":"mm"},{"id":8,"Beschreibung":"L\u00e4nge Zellf\u00e4hnchen Kathode","Wert":32.5,"Einheit":"mm"},{"id":9,"Beschreibung":"Eckenradius","Wert":5.0,"Einheit":"mm"},{"id":10,"Beschreibung":"Breite Festh\u00fclle","Wert":null,"Einheit":"mm"},{"id":11,"Beschreibung":"L\u00e4nge Festh\u00fclle","Wert":null,"Einheit":"mm"},{"id":12,"Beschreibung":"H\u00f6he Festh\u00fclle","Wert":null,"Einheit":"mm"},{"id":13,"Beschreibung":"Radius Rundzelle","Wert":10.5,"Einheit":"mm"},{"id":14,"Beschreibung":"H\u00f6he Rundzelle","Wert":70.0,"Einheit":"mm"},{"id":15,"Beschreibung":"Radius Wickelkern","Wert":3.0,"Einheit":"mm"},{"id":16,"Beschreibung":"Zusatzwicklungen Separator","Wert":3.0,"Einheit":"[-]"},{"id":17,"Beschreibung":"Abstand Separator - H\u00fclle","Wert":2.0,"Einheit":"mm"},{"id":18,"Beschreibung":"\u00dcberstand Separator - Anode","Wert":2.0,"Einheit":"mm"},{"id":19,"Beschreibung":"\u00dcberstand Anode - Kathode","Wert":2.0,"Einheit":"mm"},{"id":20,"Beschreibung":"Unterdruck Zelle","Wert":2.0,"Einheit":"mbar"},{"id":21,"Beschreibung":"Elektrolytbef\u00fcllung","Wert":80.0,"Einheit":"%"},{"id":22,"Beschreibung":"Sicherheitsabstand Schneiden","Wert":20.0,"Einheit":"mm"},{"id":23,"Beschreibung":"Beschichtungsabstand Kathode","Wert":20.0,"Einheit":"mm"},{"id":24,"Beschreibung":"Beschichtungsabstand Anode","Wert":20.0,"Einheit":"mm"},{"id":25,"Beschreibung":"Breite Kathodenkollektor","Wert":300.0,"Einheit":"mm"},{"id":26,"Beschreibung":"Breite Anodenkollektor","Wert":300.0,"Einheit":"mm"}]'
#Weitere_Zellinfos = '{"id":13,"Beschreibung":"21700","Zellformat":"Rundzelle","Dateiname":"Zelle_21700"}'

def zellberechnung(Zellchemie_raw, Materialinfos_raw, Zellformat_raw, weitere_Zellinfos_raw, GWh_Jahr_Ah_Zelle_raw):
    #____________________________________
    # allgemeine Funktionen
    # Filtert aus der gesammelten Materialinfo Tabelle ein Material heraus und gibt es als df zurück 
    def read_zellinfo(Material):
        df = Materialinfos.loc[Materialinfos["Material"] == Material]
        return df
    
    # flaeche_mit_zellf errechnet die Fäche eines Sheets mit Zellfähnchen, inklusive der Radien
    def flaeche_mit_zellf(breite, laenge, breite_zellf, laenge_zellf, radius):
        return breite*laenge+breite_zellf*laenge_zellf-(4*radius**2-math.pi*radius**2)
    def flaeche_ohne_zellf(breite, laenge, radius):
        return breite*laenge-(3*radius**2-math.pi*radius**2)
    
    
    #_________________________________ 
    # Umformen der Rohdaten in DataFrames
    a_json = json.loads(Zellchemie_raw)
    Zellchemie = pd.DataFrame.from_records(a_json)
    Zellchemie = Zellchemie.set_index('Beschreibung')
    
    
    b_json = json.loads(Materialinfos_raw)
    complete_df = []
    for Material_tabelle in b_json:
        Material = list(Material_tabelle.keys())[0]
        for Spalte in Material_tabelle[Material]:
            Spalte["Material"]=Material
            complete_df.append(Spalte)
    Materialinfos = pd.DataFrame.from_records(complete_df)
    Materialinfos = Materialinfos.set_index('Beschreibung')
    
    
    d_json = json.loads(Zellformat_raw)
    Zellformat = pd.DataFrame.from_records(d_json)
    Zellformat = Zellformat.set_index('Beschreibung')
    
    
    e_json = json.loads(weitere_Zellinfos_raw)
    weitere_Zellinfos = pd.DataFrame.from_dict(e_json, orient="index")
    Zellname = weitere_Zellinfos[0]["Beschreibung"]
    Zelltyp = weitere_Zellinfos[0]["Zellformat"]
    
    GWh_Jahr_Ah_Zelle = json.loads(GWh_Jahr_Ah_Zelle_raw)
    
    #____________________________________
    #Werte auslesen
    # Materialien auslesen
    Aktivmaterial_Kathode = Zellchemie.loc[Zellchemie['Kategorie'] == "Active material cathode"].index[0] #String
    Kollektorfolie_Kathode = Zellchemie.loc[Zellchemie['Kategorie'] == "Collector foil cathode"].index[0] #String
    Additive_Kathode = Zellchemie.loc[Zellchemie['Kategorie'] == "Additive cathode"].index.to_list() #Liste
    Lösemittel_Kathode = Zellchemie.loc[Zellchemie['Kategorie'] == "Solvent cathode"].index.to_list() #Liste
    
    Aktivmaterial_Anode = Zellchemie.loc[Zellchemie['Kategorie'] == "Active material anode"].index[0] #String
    Kollektorfolie_Anode = Zellchemie.loc[Zellchemie['Kategorie'] == "Collector foil anode"].index[0] #String
    Additive_Anode = Zellchemie.loc[Zellchemie['Kategorie'] == "Additive anode"].index.to_list() #Liste
    Lösemittel_Anode = Zellchemie.loc[Zellchemie['Kategorie'] == "Solvent anode"].index.to_list() #Liste
    
    Separator = Zellchemie.loc[Zellchemie['Kategorie'] == "Separator"].index[0] #String
    Huelle = Zellchemie.loc[Zellchemie['Kategorie'] == "Case"].index[0] #String
    
    Elektrolyt = Zellchemie.loc[Zellchemie['Kategorie'] == "Electrolyte"].index[0] #String
    
    
    #____________________________________
    #Zellchemie Parameter auslegen, gelten für alle Zellparameter
    
    U = Zellchemie["Wert"]["Cell voltage"] #Zellspannung in Volt [V]
    delta_irr = Zellchemie["Wert"]["Irreversible formation loss"] #Irreversibler Formierungsverlust in Prozent [%]
    C_flsp = Zellchemie["Wert"]["Specific areal capacity (electrode)"] #[mAh/cm²]
    
    d_KK = Materialinfos.loc[Materialinfos["Material"] == Kollektorfolie_Kathode]["Wert"]["Thickness"] #[µm]
    roh_KK = Materialinfos.loc[Materialinfos["Material"] == Kollektorfolie_Kathode]["Wert"]["Density"] #[g/cm³]
    C_sp_K = Materialinfos.loc[Materialinfos["Material"] == Aktivmaterial_Kathode]["Wert"]["Specific capacity"] #[mAh/g]
    phi_KB = Zellchemie["Wert"]["Coating porosity of cathode"] #[%]
    x_PM_K = 100-Zellchemie["Wert"][Aktivmaterial_Kathode] #Masseanteil passiver Komponenten Kathode in Prozent [%]
    
    
    d_AK = read_zellinfo(Kollektorfolie_Anode)["Wert"]["Thickness"] #[µm]   
    roh_AK = read_zellinfo(Kollektorfolie_Anode)["Wert"]["Density"] #[g/cm³]
    C_sp_A = read_zellinfo(Aktivmaterial_Anode)["Wert"]["Specific capacity"] #[mAh/g]
    phi_AB = Zellchemie["Wert"]["Coating porosity of anode"] #[%]
    x_PM_A = 100-Zellchemie["Wert"][Aktivmaterial_Anode] #Masseanteil passiver Komponenten Anode in Prozent [%]
    delta_A = Zellchemie["Wert"]["Calculated anode excess"] #[%]
     
    d_Sep = read_zellinfo(Separator)["Wert"]["Thickness"] #[µm]
    roh_sep = read_zellinfo(Separator)["Wert"]["Density"] #[g/cm³]
    phi_sep = read_zellinfo(Separator)["Wert"]["Porosity"] #[%]
    
    roh_elyt = read_zellinfo(Elektrolyt)["Wert"]["Density"] #[g/cm³]

    Wandstaerke = read_zellinfo(Huelle)["Wert"]["Thickness"] #[mm]
    
    
    #____________________________________
    #Zusammensetzung der Suspension auslesen, Kosten/ Dichte berechnen
    
    Bestandteile_Loesemittel_Anode =  Zellchemie.loc[Zellchemie['Kategorie'] == "Solvent anode"].index.to_list() #Liste
    Kosten_Loesemittel_Anode = sum(Zellchemie["Wert"][x]/100*read_zellinfo(x)["Wert"]["Price"]*(1-read_zellinfo(x)["Wert"]["Reusable share"]/100) for x in Bestandteile_Loesemittel_Anode)

    Bestandteile_Anodenbeschichtung = Additive_Anode #ohne Lösemittel
    Bestandteile_Anodenbeschichtung.append(Aktivmaterial_Anode) #ohne Lösemittel
    Gesamtdichte_Anodenfeststoffe = 1/sum(Zellchemie["Wert"][x]/100/read_zellinfo(x)["Wert"]["Density"] for x in Bestandteile_Anodenbeschichtung)
    Gesamtdichte_Anodenlösemittel = 1/sum(Zellchemie["Wert"][x]/100/read_zellinfo(x)["Wert"]["Density"] for x in Lösemittel_Anode)
    Gesamtdichte_Anodenbeschichtung = 1/(Zellchemie["Wert"]["Solid content of anode"]/100/Gesamtdichte_Anodenfeststoffe + (1-Zellchemie["Wert"]["Solid content of anode"]/100)/Gesamtdichte_Anodenlösemittel)
    
    Kosten_Anodenbeschichtung = sum(Zellchemie["Wert"][x]/100*read_zellinfo(x)["Wert"]["Price"] for x in Bestandteile_Anodenbeschichtung) #€/kg
    Kosten_Anodenkollektor = read_zellinfo(Kollektorfolie_Anode)["Wert"]["Price"] #[€/m²]
        
    Bestandteile_Loesemittel_Kathode =  Zellchemie.loc[Zellchemie['Kategorie'] == "Solvent cathode"].index.to_list() #Liste
    Kosten_Loesemittel_Kathode = sum(Zellchemie["Wert"][x]/100*read_zellinfo(x)["Wert"]["Price"]*(1-read_zellinfo(x)["Wert"]["Reusable share"]/100) for x in Bestandteile_Loesemittel_Kathode)

    Bestandteile_Kathodenbeschichtung=Additive_Kathode #ohne Lösemittel
    Bestandteile_Kathodenbeschichtung.append(Aktivmaterial_Kathode) 
    Gesamtdichte_Kathodenfeststoffe = 1/sum(Zellchemie["Wert"][x]/100/read_zellinfo(x)["Wert"]["Density"] for x in Bestandteile_Kathodenbeschichtung)
    Gesamtdichte_Kathodenlösemittel = 1/sum(Zellchemie["Wert"][x]/100/read_zellinfo(x)["Wert"]["Density"] for x in Lösemittel_Kathode)
    Gesamtdichte_Kathodenbeschichtung = 1/(Zellchemie["Wert"]["Solid content of cathode"]/100/Gesamtdichte_Kathodenfeststoffe + (1-Zellchemie["Wert"]["Solid content of cathode"]/100)/Gesamtdichte_Kathodenlösemittel)
    
    Kosten_Kathodenbeschichtung = sum(Zellchemie["Wert"][x]/100*read_zellinfo(x)["Wert"]["Price"] for x in Bestandteile_Kathodenbeschichtung) #€/kg
    Kosten_Kathodenkollektor = read_zellinfo(Kollektorfolie_Kathode)["Wert"]["Price"] #[€/m²]
                
    Kosten_Separator = read_zellinfo(Separator)["Wert"]["Price"] #[€/m²]
    Kosten_Elektrolyt = read_zellinfo(Elektrolyt)["Wert"]["Price"] #[€/kg]
            
    GWh_pro_jahr = GWh_Jahr_Ah_Zelle["GWh_pro_jahr"] #[-]
    
    roh_KB = Gesamtdichte_Kathodenfeststoffe*(1-phi_KB/100) #[g/cm³]
    roh_AB = Gesamtdichte_Anodenfeststoffe*(1-phi_AB/100) #[g/cm³]

    
    #____________________________________
    # Elektrochemische Charakterisierung, gleich für alle Zelltypen
    
    MB_K = C_flsp/(1-delta_irr/100)/(C_sp_K*(1-x_PM_K/100)) #Massenbelegung Kathode [g/cm²]
    MB_A = C_flsp*(1+delta_A/100)/(C_sp_A*(1-x_PM_A/100)) #Massenbelegung Anode [g/cm²]

    d_KB = (MB_K/roh_KB)*10000 #Dicke Kathodenbeschichtung [µm]
    d_AB = (MB_A/roh_AB)*10000 #Dicke Anodenbeschichtung [µm]
    d_WHE = d_AK + 2*d_AB + d_KK + 2*d_KB + 2*d_Sep #Dicke einer Wiederholeinheit [µm]
    d_MWHE = d_AK + 2*d_AB + 2*d_Sep #Dicke modifizierte Wiederholeinheit [µm]
    
    
    #____________________________________
    #Zellmaße die für alle Zellen gelten
    
    elektrolytbefuellung = Zellformat["Wert"]["Electrolyte filling factor"] #[%]

    Breite_Kathodenkollektor = read_zellinfo(Kollektorfolie_Kathode)["Wert"]["Width"] #[mm]
    Breite_Anodenkollektor = read_zellinfo(Kollektorfolie_Anode)["Wert"]["Width"] #[mm]
    Breite_Separator = read_zellinfo(Separator)["Wert"]["Width"] #[mm]
    
    
    #____________________________________
    # Ab hier die Berechnung der einzelnen Zelltypen
        
    if Zelltyp == "Cylindrical cell":
        Wandstärke = Wandstaerke #[mm]
        #Außenmaße der Runzelle
        radius_rundzelle = Zellformat["Wert"]["Cell radius of cylindrical cell"]-Wandstärke #[mm]
        hoehe_rundzelle = Zellformat["Wert"]["Height of cylindrical cell"]-2*Wandstärke #[mm]
                                
        A_Huelle = 2*math.pi*radius_rundzelle*hoehe_rundzelle+math.pi*2*radius_rundzelle**2

        abs_zellwickel_deckel = Zellformat["Wert"]["Distance from roll to cap"] #[mm]
        
        Beschichtungsabstand_Kathode = Zellformat["Wert"]["Coating distance cathode"] #[mm]
        Beschichtungsabstand_Anode = Zellformat["Wert"]["Coating distance anode"] #[mm]

        #Innenabstände der Separatoren
        ueberstand_separator_anode = Zellformat["Wert"]["Projection separator to anode"] #[mm]
        ueberstand_anode_kathode = Zellformat["Wert"]["Projection anode to cathode"] #[mm]

        #Zellableiter
        Abl_in_Zelle_A = ueberstand_separator_anode+Zellformat["Wert"]["Length of anode arrester in cell"] #[mm]
        Abl_in_Zelle_K = ueberstand_separator_anode+ueberstand_anode_kathode+Zellformat["Wert"]["Length of cathode arrester in cell"] #[mm]
        
        #Weitere Angaben Rundzelle
        sep_wick = Zellformat["Wert"]["Additional layers separator"] #zusätzliche Separatorwicklungen
        r_w = Zellformat["Wert"]["Radius of winding core"] #[mm] Radius Wickelkern

        #l_bahn beschreibt die länge des Anoden-Kathodenverbundes ohne Separatorüberstand, also die Anodenlänge
        l_bahn = ((radius_rundzelle-2*sep_wick*d_Sep/1000)**2-(r_w+2*sep_wick*d_Sep/1000)**2)*math.pi/(d_WHE/1000) #[mm]
               
        #Annahme: Ableiter umgeknickt und dementsprechend kein Platz benötigt. 
        A_KK = (hoehe_rundzelle-abs_zellwickel_deckel-2*ueberstand_separator_anode-2*ueberstand_anode_kathode+Abl_in_Zelle_K)*(l_bahn-2*ueberstand_anode_kathode)
        A_KB = (hoehe_rundzelle-abs_zellwickel_deckel-2*ueberstand_separator_anode-2*ueberstand_anode_kathode)*(l_bahn-2*ueberstand_anode_kathode)
        A_AK = (hoehe_rundzelle-abs_zellwickel_deckel-2*ueberstand_separator_anode+Abl_in_Zelle_A)*(l_bahn)
        A_AB = (hoehe_rundzelle-abs_zellwickel_deckel-2*ueberstand_separator_anode)*(l_bahn)
        
        A_sep_innen = 0
        A_sep_aussen = 0
        for no_wick in range(int(sep_wick)):
            A_sep_innen+=(hoehe_rundzelle-abs_zellwickel_deckel)*2*math.pi*(r_w+(no_wick+0.5)*2*d_Sep/1000)
            A_sep_aussen+=(hoehe_rundzelle-abs_zellwickel_deckel)*2*math.pi*(radius_rundzelle-(no_wick+0.5) *2*d_Sep/1000)
            
        A_Sep = l_bahn*(hoehe_rundzelle-abs_zellwickel_deckel)+A_sep_innen+A_sep_aussen #Fläche Separator [mm²]

        l_WHE = C_flsp*A_KB*2/100 #[mAh] Ladung einer Wiederholeinheit (doppelt beschichtete Kathode -> *2)

        anzahl_WHE = 1
        
        A_AB_ges = A_AB*2
        A_KB_ges = A_KB*2
        A_AK_ges = A_AK
        A_KK_ges = A_KK
        A_Sep_ges = A_Sep*2

        #Meter Elektrode/Sheet
        #Anzahl Sheets übereinander (beschichtete Bahnen), normal (für Ausnutzungsgrad) und abgerundet & Sheets pro meter Elektrode (S_MA & S_MK)
        #Anode
        bahnen_bes_A_ausn = (Breite_Anodenkollektor)/(hoehe_rundzelle-abs_zellwickel_deckel-2*ueberstand_separator_anode+Beschichtungsabstand_Anode)
        bahnen_bes_A = math.floor(bahnen_bes_A_ausn)
        if (bahnen_bes_A % 2) != 0 and bahnen_bes_A != 1:
            bahnen_bes_A = bahnen_bes_A-1
        bahnen_bes_A_ausn = round(bahnen_bes_A/bahnen_bes_A_ausn,4)*100
        S_MA = 1000/(l_bahn)*bahnen_bes_A

        #Kathode
        bahnen_bes_K_ausn = (Breite_Kathodenkollektor)/(hoehe_rundzelle-abs_zellwickel_deckel-2*ueberstand_separator_anode-2*ueberstand_anode_kathode+Beschichtungsabstand_Kathode)
        bahnen_bes_K = math.floor(bahnen_bes_K_ausn)
        if (bahnen_bes_K % 2) != 0 and bahnen_bes_K != 1:
            bahnen_bes_K = bahnen_bes_K-1
        bahnen_bes_K_ausn = round(bahnen_bes_K/bahnen_bes_K_ausn,4)*100
        S_MK = 1000/(l_bahn-2*ueberstand_anode_kathode)*bahnen_bes_K

        vol_nutz_zelle = math.pi*radius_rundzelle*radius_rundzelle*hoehe_rundzelle #[mm³]
    
    if Zelltyp == "Flat wound hardcase":
        #Außenmaße der Zelle
        Wandstärke = Wandstaerke #[mm]


        breite_festhuelle = Zellformat["Wert"]["Width of the hardcase"]-2*Wandstärke #[mm]
        laenge_festhuelle = Zellformat["Wert"]["Length of the hardcase"]-2*Wandstärke #[mm]
        hoehe_festhuelle = Zellformat["Wert"]["Height of the hardcase"]-2*Wandstärke #[mm]

        A_Huelle = 2*breite_festhuelle*laenge_festhuelle+2*breite_festhuelle*hoehe_festhuelle+2*laenge_festhuelle*hoehe_festhuelle

        Beschichtungsabstand_Kathode = Zellformat["Wert"]["Coating distance cathode"] #[mm]
        Beschichtungsabstand_Anode = Zellformat["Wert"]["Coating distance anode"] #[mm]
        #Innenabstände der Separatoren
        ueberstand_separator_anode = Zellformat["Wert"]["Projection separator to anode"] #[mm]
        ueberstand_anode_kathode = Zellformat["Wert"]["Projection anode to cathode"] #[mm]
        abs_zellwickel_deckel = Zellformat["Wert"]["Distance from roll to cap"] #[mm]
        abs_ableiter_huelle = Zellformat["Wert"]["Distance from arrester to case"] #[mm]

        #Zellableiter
        Abl_in_Zelle_A = ueberstand_separator_anode+Zellformat["Wert"]["Length of anode arrester in cell"] #[mm]
        Abl_in_Zelle_K = ueberstand_separator_anode+ueberstand_anode_kathode+Zellformat["Wert"]["Length of cathode arrester in cell"] #[mm]

        #Weitere Angaben Prismatische Zelle
        sep_wick = Zellformat["Wert"]["Additional layers separator"] #zusätzliche Separatorwicklungen
        r_w = Zellformat["Wert"]["Radius of winding core"] #[mm] Radius Wickelkern

        #Anzahl Wicklungen
        Anz_wick = ((laenge_festhuelle-2*r_w)/2-(4*sep_wick*d_Sep/1000))/(d_WHE/1000) #[-]

        #Breite des Wickelkerns
        Breite_Kern = hoehe_festhuelle-4*sep_wick*d_Sep/1000-2*Anz_wick*d_WHE/1000-abs_zellwickel_deckel-2*r_w #[mm]
        
        A_wickel_querschnitt = Breite_Kern*2*Anz_wick*d_WHE/1000+( (r_w+2*sep_wick*d_Sep/1000+Anz_wick*d_WHE/1000)**2 - (r_w+2*sep_wick*d_Sep/1000)**2)*math.pi #[mm^2]
        l_bahn = A_wickel_querschnitt/d_WHE*1000 #[mm]

        A_KK = (l_bahn-2*ueberstand_anode_kathode)*(breite_festhuelle-ueberstand_anode_kathode-Abl_in_Zelle_A-abs_ableiter_huelle*2)
        A_KB = (l_bahn-2*ueberstand_anode_kathode)*(breite_festhuelle-ueberstand_anode_kathode-Abl_in_Zelle_A-Abl_in_Zelle_A-abs_ableiter_huelle*2)
        A_AK = (l_bahn)*(breite_festhuelle+ueberstand_anode_kathode-Abl_in_Zelle_K-abs_ableiter_huelle*2)
        A_AB = (l_bahn)*(breite_festhuelle+ueberstand_anode_kathode-Abl_in_Zelle_K-Abl_in_Zelle_A-abs_ableiter_huelle*2)

        breite_sep = breite_festhuelle-abs_ableiter_huelle*2-Abl_in_Zelle_A-Abl_in_Zelle_K+2*ueberstand_separator_anode+ueberstand_anode_kathode        
        A_Sep_inner = (Breite_Kern*4*d_Sep/1000*sep_wick + ((r_w+2*d_Sep/1000*sep_wick)**2 - r_w**2)*math.pi)/(d_Sep/1000)*breite_sep
        A_Sep_outer = (Breite_Kern*4*d_Sep/1000*sep_wick + ((laenge_festhuelle/2)**2 - (laenge_festhuelle/2-2*d_Sep/1000*sep_wick)**2)*math.pi)/(d_Sep/1000)*breite_sep
        
    
        A_Sep = l_bahn*breite_sep

        l_WHE = C_flsp*A_KB*2/100 #[mAh] Ladung einer Wiederholeinheit (doppelt beschichtete Kathode -> *2)

        anzahl_WHE = 1
        
        A_AB_ges = A_AB*2
        A_KB_ges = A_KB*2
        A_AK_ges = A_AK
        A_KK_ges = A_KK
        A_Sep_ges = A_Sep*2+ A_Sep_inner+A_Sep_outer
              
        #Meter Elektrode/Sheet
        #Anzahl Sheets übereinander (beschichtete Bahnen), normal (für Ausnutzungsgrad) und abgerundet & Sheets pro meter Elektrode (S_MA & S_MK)
        #Anode
        bahnen_bes_A_ausn = (Breite_Anodenkollektor)/(breite_festhuelle+ueberstand_anode_kathode-Abl_in_Zelle_K-Abl_in_Zelle_A-abs_ableiter_huelle*2+Beschichtungsabstand_Anode)
        
        bahnen_bes_A = math.floor(bahnen_bes_A_ausn)
        if (bahnen_bes_A % 2) != 0 and bahnen_bes_A != 1:
            bahnen_bes_A = bahnen_bes_A-1
        bahnen_bes_A_ausn = round(bahnen_bes_A/bahnen_bes_A_ausn,4)*100
        S_MA = 1000/(l_bahn)*bahnen_bes_A

        #Kathode
        bahnen_bes_K_ausn = (Breite_Kathodenkollektor)/(breite_festhuelle-ueberstand_anode_kathode-Abl_in_Zelle_K-Abl_in_Zelle_A-abs_ableiter_huelle*2+Beschichtungsabstand_Kathode)
        
        bahnen_bes_K = math.floor(bahnen_bes_K_ausn)
        if (bahnen_bes_K % 2) != 0 and bahnen_bes_K != 1:
            bahnen_bes_K = bahnen_bes_K-1
        bahnen_bes_K_ausn = round(bahnen_bes_K/bahnen_bes_K_ausn,4)*100
        S_MK = 1000/(l_bahn-2*ueberstand_anode_kathode)*bahnen_bes_K
        
        vol_nutz_zelle = breite_festhuelle * laenge_festhuelle * hoehe_festhuelle #[mm³]
        
    #____________________________________
    # Ab hier wieder gesammelte Berechnung für alle Zelltypen
    
    #Gewichte der Einzelsheets jeweils & Gewicht der gesamten WHE
    gew_AK = A_AK*d_AK*roh_AK/1000000 #[g]
    gew_AB = A_AB*d_AB*roh_AB/1000000 #[g], einzeln
    gew_KK = A_KK*d_KK*roh_KK/1000000 #[g]
    gew_KB = A_KB*d_KB*roh_KB/1000000 #[g], einzeln
    gew_Sep = A_Sep*d_Sep*roh_sep/1000000 #[g]
    gew_WHE = gew_AK+2*gew_AB+gew_KK+2*gew_KB+2*gew_Sep
    gew_MWHE = gew_AK+2*gew_AB+2*gew_Sep
    
    #Volumina der Einzelsheets
    vol_sep = A_Sep_ges * d_Sep/1000 #[mm³]
    vol_AB = A_AB * d_AB/1000 #[mm³]
    vol_AK = A_AK * d_AK/1000 #[mm³]
    vol_KB = A_KB * d_KB/1000 #[mm³]
    vol_KK = A_KK * d_KK/1000 #[mm³]
    
    #Volumen und Gewicht des Elektrolyts
    vol_elyt = vol_sep * phi_sep/100 + vol_AB*2 * phi_AB/100 + vol_KB*2 * phi_KB/100 + (vol_nutz_zelle - (vol_sep + vol_AB*2 + vol_AK + vol_KB*2 + vol_KK)*anzahl_WHE)*elektrolytbefuellung/100 #[mm³]
    gew_elyt = vol_elyt*roh_elyt/1000 #[g]

    volumenfaktor = vol_elyt/(vol_sep * phi_sep/100 + vol_AB*2 * phi_AB/100 + vol_KB*2 * phi_KB/100)

    gew_huelle = read_zellinfo(Huelle)["Wert"]["Weight"] #[g]
    
    #die Gesamtgewichte der Einzelbestandteile 
    #gewickelte Zellen haben keine modifizierte Wiederholeinheit, gestapelte Zellen schon
    
    if Zelltyp == "Cylindrical cell" or Zelltyp == "Flat wound hardcase":
        gew_AK_ges = gew_AK*anzahl_WHE #[g] 
        gew_AB_ges = gew_AB*anzahl_WHE*2 #[g] *2 für die doppelseitige Beschichtung 
        gew_KK_ges = gew_KK*anzahl_WHE #[g]
        gew_KB_ges = gew_KB*anzahl_WHE*2 #[g] *2 für die doppelseitige Beschichtung 
        gew_Sep_ges = gew_Sep*anzahl_WHE*2 #[g] *2, da eine WHE 2 Separator Blätter enthält
        gew_ges = gew_elyt + gew_WHE * anzahl_WHE + gew_huelle
       
    
    #Gesamtladung einer Zelle, Anzahl zu produzierender Zellen/ Jahr, spezifische Ladungsdichte einer Zelle
    Q_ges = l_WHE*anzahl_WHE/1000 #gesamte Ladung einer Zelle in Ah
    Zellen_pro_Jahr = GWh_pro_jahr*1000000000/(Q_ges*U) #*1 Mrd wegen Giga
    spez_energie = U*Q_ges*1000/gew_ges #[Wh/kg] *1000 -> Gewicht Zelle g zu kg
    Balancing = (1-(A_KB*C_flsp)/(A_AB*C_flsp))*100

    Kosten_Huelle = read_zellinfo(Huelle)["Wert"]["Price"] #[€/m²]
    
    #Auflistung aller Kosten einer Zelle
    Gesamtkosten_Loesemittel_Anode = Kosten_Loesemittel_Anode * gew_AB_ges/1000 * (1-(Zellchemie["Wert"]["Solid content of anode"]/100))
    Gesamtkosten_Loesemittel_Kathode = Kosten_Loesemittel_Kathode * gew_KB_ges/1000 * (1-(Zellchemie["Wert"]["Solid content of cathode"]/100))

    #Gesamtkosten_Anodenbeschichtung = Kosten_Anodenbeschichtung * gew_AB_ges/1000 + Gesamtkosten_Loesemittel_Anode #[€]
    Gesamtkosten_Anodenbeschichtung = Kosten_Anodenbeschichtung * gew_AB_ges/1000 #[€]
    #Gesamtkosten_Kathodenbeschichtung = Kosten_Kathodenbeschichtung * gew_KB_ges/1000 + Gesamtkosten_Loesemittel_Kathode #[€]
    Gesamtkosten_Kathodenbeschichtung = Kosten_Kathodenbeschichtung * gew_KB_ges/1000  #[€]

    Gesamtkosten_Anodenkollektor = Kosten_Anodenkollektor * A_AK_ges / 1000000 #[€]
    Gesamtkosten_Kathodenkollektor = Kosten_Kathodenkollektor * A_KK_ges / 1000000 #[€]
    Gesamtkosten_Huelle = Kosten_Huelle
    #Gesamtkosten_Huelle = Kosten_Huelle * A_Huelle /1e6
    Gesamtkosten_Separator = Kosten_Separator * A_Sep_ges / 1000000
    Gesamtkosten_Elektrolyt = Kosten_Elektrolyt * gew_elyt/1000 #[€]
    Gesamtkosten_Zelle = (Gesamtkosten_Anodenbeschichtung 
                        + Gesamtkosten_Kathodenbeschichtung 
                        + Gesamtkosten_Anodenkollektor 
                        + Gesamtkosten_Kathodenkollektor 
                        + Gesamtkosten_Huelle
                        + Gesamtkosten_Separator
                        + Gesamtkosten_Elektrolyt
                        )
    
    #____________________________________
    # Ab hier der Export aller Informationen
    

                       
    
    export_zellberechnung = [
        
        {"Beschreibung":"Capacity","Wert":round(Q_ges,2),"Einheit":"Ah","Kategorie":"Overview"},
        {"Beschreibung":"Cell format","Wert":Zellname,"Einheit":"","Kategorie":"Overview"},
        {"Beschreibung":"Cell type","Wert":Zelltyp,"Einheit":"","Kategorie":"Overview"},
        {"Beschreibung":"Nominal voltage","Wert":U,"Einheit":"V","Kategorie":"Overview"},
        {"Beschreibung":"Energy density","Wert":round(spez_energie,2),"Einheit":"Wh/kg","Kategorie":"Overview"},
        {"Beschreibung":"Cells per year","Wert":round(Zellen_pro_Jahr,2),"Einheit":"","Kategorie":"Overview"},
        {"Beschreibung":"Weight of a cell","Wert":round(gew_ges,3),"Einheit":"g","Kategorie":"Overview"},
        {"Beschreibung":"Volume factor","Wert":round(volumenfaktor,2),"Einheit":"-","Kategorie":"Overview"},
        
        #{"Beschreibung":"Balancing","Wert":round(Balancing,2),"Einheit":"%","Kategorie":"Übersicht"},
        
        {"Beschreibung":"Number of repeating units","Wert":anzahl_WHE,"Einheit":"","Kategorie":"Dimensions and areas"},
        {"Beschreibung":"Total area of anode coating","Wert":round(A_AB_ges,2),"Einheit":"mm²","Kategorie":"Dimensions and areas"},
        {"Beschreibung":"Total cathode coating area","Wert":round(A_KB_ges,2),"Einheit":"mm²","Kategorie":"Dimensions and areas"},
        {"Beschreibung":"Total area of separator","Wert":round(A_Sep_ges,2),"Einheit":"mm²","Kategorie":"Dimensions and areas"},
        {"Beschreibung":"Balancing","Wert":round(Balancing,2),"Einheit":"%","Kategorie":"Dimensions and areas"},
        
        {"Beschreibung":"Areal mass of anode coating","Wert":MB_A*1000,"Einheit":"mg/cm²","Kategorie":"Weights and densities"},
        {"Beschreibung":"Areal mass of cathode coating","Wert":MB_K*1000,"Einheit":"mg/cm²","Kategorie":"Weights and densities"},
        {"Beschreibung":"Density of the anode coating","Wert":round(Gesamtdichte_Anodenbeschichtung,2),"Einheit":"g/cm³","Kategorie":"Weights and densities"},
        {"Beschreibung":"Density of the cathode coating","Wert":round(Gesamtdichte_Kathodenbeschichtung,2),"Einheit":"g/cm³","Kategorie":"Weights and densities"},
        {"Beschreibung":"Weight of the anode collector","Wert":round(gew_AK_ges,2),"Einheit":"g","Kategorie":"Weights and densities"},
        {"Beschreibung":"Weight of the cathode collector","Wert":round(gew_KK_ges,2),"Einheit":"g","Kategorie":"Weights and densities"},
        {"Beschreibung":"Weight of the anode coating","Wert":round(gew_AB_ges,2),"Einheit":"g","Kategorie":"Weights and densities"},
        {"Beschreibung":"Weight of the cathode coating","Wert":round(gew_KB_ges,2),"Einheit":"g","Kategorie":"Weights and densities"},
        {"Beschreibung":"Weight of the separator","Wert":round(gew_Sep_ges,2),"Einheit":"g","Kategorie":"Weights and densities"},
        {"Beschreibung":"Weight of the electrolyte","Wert":round(gew_elyt,2),"Einheit":"g","Kategorie":"Weights and densities"},
        {"Beschreibung":"Weight of the case","Wert":round(gew_huelle,2),"Einheit":"g","Kategorie":"Weights and densities"},
        {"Beschreibung":"Weight of a cell","Wert":round(gew_ges,2),"Einheit":"g","Kategorie":"Weights and densities"},
        
        {"Beschreibung":"Cost per kilogram anode coating","Wert":round(Kosten_Anodenbeschichtung + Kosten_Loesemittel_Anode,2),"Einheit":"$/kg","Kategorie":"Costs"},
        {"Beschreibung":"Cost per kilogram cathode coating","Wert":round(Kosten_Kathodenbeschichtung + Kosten_Loesemittel_Kathode,2),"Einheit":"$/kg","Kategorie":"Costs"},
        {"Beschreibung":"Cost of the anode coating","Wert":round(Gesamtkosten_Anodenbeschichtung,2),"Einheit":"$","Kategorie":"Costs"},
        {"Beschreibung":"Cost of the cathode coating","Wert":round(Gesamtkosten_Kathodenbeschichtung,2),"Einheit":"$","Kategorie":"Costs"},
        {"Beschreibung":"Cost of the anode collector","Wert":round(Gesamtkosten_Anodenkollektor,2),"Einheit":"$","Kategorie":"Costs"},
        {"Beschreibung":"Cost of the cathode collector","Wert":round(Gesamtkosten_Kathodenkollektor,2),"Einheit":"$","Kategorie":"Costs"},
        {"Beschreibung":"Cost of the separator","Wert":round(Gesamtkosten_Separator,2),"Einheit":"$","Kategorie":"Costs"},
        {"Beschreibung":"Cost of the electrolyte","Wert":round(Gesamtkosten_Elektrolyt,2),"Einheit":"$","Kategorie":"Costs"},
        {"Beschreibung":"Cost of the hardcase","Wert":round(Gesamtkosten_Huelle,2),"Einheit":"$","Kategorie":"Costs"},
        {"Beschreibung":"Material cost of a cell","Wert":round(Gesamtkosten_Zelle,2),"Einheit":"$","Kategorie":"Costs"},
        
        {"Beschreibung":"Yield of anode coating","Wert":bahnen_bes_A_ausn,"Einheit":"%","Kategorie":"Used area in the electrode"},
        {"Beschreibung":"Anode coating","Wert":bahnen_bes_A,"Einheit":"No. of sheets","Kategorie":"Used area in the electrode"},
        {"Beschreibung":"Sheets/meter anode","Wert":S_MA,"Einheit":"Sheet/m","Kategorie":"Used area in the electrode"},
        {"Beschreibung":"Yield of cathode coating","Wert":bahnen_bes_K_ausn,"Einheit":"%","Kategorie":"Used area in the electrode"},
        {"Beschreibung":"Cathode coating","Wert":bahnen_bes_K,"Einheit":"No. of sheets","Kategorie":"Used area in the electrode"},
        {"Beschreibung":"Sheets/meter cathode","Wert":S_MK,"Einheit":"Sheet/m","Kategorie":"Used area in the electrode"},
            ]
    
    return (pd.DataFrame(export_zellberechnung))



#zellberechnung(Zellchemie, Materialinfos, Zellformat, Weitere_Zellinfos)
