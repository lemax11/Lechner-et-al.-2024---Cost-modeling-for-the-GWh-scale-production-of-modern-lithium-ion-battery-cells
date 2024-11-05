# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 21:39:53 2021

@author: Lukas Kemmer
"""

#### Levelized cost of battery cells calculator ####

import pandas as pd
import numpy as np

# Settings
pd.options.mode.chained_assignment = None  # default='warn'

def levelized_cost(construction_cost_factory,
                   lifetime_factory,
                   interest_rate,
                   tax_rate,
                   Materialkosten,
                   Materialkosten_mit_rueckgewinnung,
                   Personalkosten,
                   Energiekosten,
                   fix_cost,
                   output_kWh,
                   machine_invest,
                   factory_depreciation,
                   machine_depreciation,
                   ramp_up_material,
                   ramp_up_personal_overhead
                   ):
        
    variable_cost = Materialkosten+Energiekosten+Personalkosten
    output_kWh = int(output_kWh)
    machine_invest = int(machine_invest)
    factory_depreciation = int(factory_depreciation)
    machine_depreciation = int(machine_depreciation)
    lifetime_factory = int(lifetime_factory)
    ramp_up_cost = Materialkosten * ramp_up_material /100 + (Personalkosten + fix_cost) * ramp_up_personal_overhead / 100


    ## Create dataframe


    # Create depreciation schedule based on linear depriciation
    d_i = np.full(shape=lifetime_factory+1, fill_value=0, dtype=np.float)
    d_i[1:factory_depreciation+1] = 1/factory_depreciation * construction_cost_factory # factory depreciation
    d_i[1:lifetime_factory+1] = d_i[1:lifetime_factory+1] + np.full(shape=lifetime_factory, fill_value=machine_invest/machine_depreciation, dtype=np.float)


    # Create investment array
    I_i = np.full(shape=lifetime_factory+1, fill_value=0, dtype=np.float)
    I_i[0::machine_depreciation] = machine_invest
    I_i[0] = I_i[0] + construction_cost_factory + ramp_up_cost
    I_i[lifetime_factory] = 0

    # Create data frame with all parameters
    data = {
            'year' : np.arange(0,lifetime_factory+1),
            'w_i' : np.full(shape=lifetime_factory+1, fill_value=variable_cost, dtype=np.float),
            'w_i_rueckgewinnung' : np.full(shape=lifetime_factory+1, fill_value=(Materialkosten_mit_rueckgewinnung+Energiekosten+Personalkosten), dtype=np.float),
            'f_i' : np.full(shape=lifetime_factory+1, fill_value=fix_cost, dtype=np.float),
            'o_i' : np.full(shape=lifetime_factory+1, fill_value=output_kWh, dtype=np.float),
            'd_i' : d_i,
            'I_i' : I_i
            }

    var_params = pd.DataFrame(data)
    # Set variable and fixed cost and output to 0 for period 0 (production starts in period 1)

    var_params['o_i'][0] = 0
    var_params['f_i'][0] = 0
    var_params['w_i'][0] = 0
    var_params['w_i_rueckgewinnung'][0] = 0

    ## Calculation

    # Set gamma
    gamma = 1/(1+interest_rate)

    # Calc levelized output, o
    var_params['o_helper'] = var_params['o_i'] * np.power(gamma, var_params['year'])
    o = var_params['o_helper'].sum()

    # Calc levelized var cost, w
    var_params['w_helper'] = var_params['w_i'] * np.power(gamma, var_params['year'])
    w = var_params['w_helper'].sum() / o

    # Calc levelized var cost, w Rückgewinnung
    var_params['w_rueck_helper'] = var_params['w_i_rueckgewinnung'] * np.power(gamma, var_params['year'])
    w_rueck = var_params['w_rueck_helper'].sum() / o

    # Calc levelized fixed cost, f
    var_params['f_helper'] = var_params['f_i'] * np.power(gamma, var_params['year'])
    f = var_params['f_helper'].sum() / o

    # Calc depreciation (absolute, discounted per year)
    var_params['d_helper'] = var_params['d_i'] * np.power(gamma, var_params['year'])

    # Calc investment (absolute, discounted per year)
    var_params['I_helper'] = var_params['I_i'] * np.power(gamma, var_params['year'])

    # Calc levelized cost of battery cells (LCOB), lc_b
    lc_b = w + f + (var_params['I_helper'].sum()- tax_rate * var_params['d_helper'].sum()) / ((1-tax_rate)*o)

    # Calc levelized cost of battery cells (LCOB), lc_b Rückgewinnung
    lc_b_rueckgewinnung = w_rueck + f + (var_params['I_helper'].sum()- tax_rate * var_params['d_helper'].sum()) / ((1-tax_rate)*o)

    # Calculate marginal cost of batteries
    mc_b = variable_cost / output_kWh

    # Calculate marginal cost of batteries
    mc_b_rueckgewinnung = (Materialkosten_mit_rueckgewinnung+Energiekosten+Personalkosten) / output_kWh

    # Calculate full cost of batteries
    fc_b = (variable_cost + fix_cost + construction_cost_factory/factory_depreciation + machine_invest / machine_depreciation + ramp_up_cost / lifetime_factory) / output_kWh

    # Calculate full cost of batteries
    fc_b_rueckgewinnung = (Materialkosten_mit_rueckgewinnung+Energiekosten+Personalkosten + fix_cost + construction_cost_factory/factory_depreciation + machine_invest / machine_depreciation + ramp_up_cost / lifetime_factory) / output_kWh

    ## Output results

    #print('LCOB = ', round(lc_b, 4), ' EUR / kWh')

    #print('MC = ', round(mc_b, 4), ' EUR / kWh')

    #print('FC = ', round(fc_b, 4), ' EUR / kWh')

    full_cost_aufgeteilt = [
        {
            "group": "Material",
            "value":  Materialkosten,
        },
        {
            "group": "Personal",
            "value":  Personalkosten
        },
        {
            "group": "Energy",
            "value":  Energiekosten
        },
        {
            "group": "Depreciation",
            "value": construction_cost_factory/factory_depreciation + machine_invest / machine_depreciation + ramp_up_cost / lifetime_factory
        },
        {
            "group": "Overhead",
            "value": fix_cost
        }
    ]

    return {"levelized_cost":round(lc_b,2),
            "marginal_cost":round(mc_b,2), 
            "full_cost":round(fc_b, 2),
            "levelized_cost_rueckgewinnung":round(lc_b_rueckgewinnung,2),
            "marginal_cost_rueckgewinnung":round(mc_b_rueckgewinnung,2), 
            "full_cost_rueckgewinnung":round(fc_b_rueckgewinnung, 2)},full_cost_aufgeteilt


