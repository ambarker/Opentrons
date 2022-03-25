import csv

metadata = {
    'protocolName': 'Standardize DNA Concentrations',
    'author': 'AMB, last updated 3/25/22',
    'description': 'Standardize samples to target DNA concentration by adding designated amounts of DNA '
                   'and water to wells.',
    'apiLevel': '2.11'
}


def run(protocol):
    ########## EDIT THESE RUN OPTIONS AS NEEDED ##########

    # location of p300 single channel ('left' or 'right', all lowercase and in single quotes)
    pipette_mount_300 = 'left'

    # location of p20 single channel ('left' or 'right', all lowercase and in single quotes)
    pipette_mount_20 = 'right'

    # number of source (DNA) plates (integar, min: 1 max: 3)
    num_source_plates = 3

    # number of destination (standardized) plates (integar, min: 1 max: 2)
    num_destination_plates = 2

    # source plate type ('biorad_200ul' or 'nest_100ul', all lowercase and in single quotes)
    source_plate_type = 'nest_100ul'

    # destination plate type ('biorad_200ul' or 'nest_100ul', all lowercase and in single quotes)
    destination_plate_type = 'biorad_200ul'

    # pre-used or fresh destination plate ('used' or 'fresh', all lowercase and in single quotes)
    destination_plate_status = 'used'

    # 3rd tip rack type ('20','300', or 'none',  in single quotes)
    extra_rack_type = 'none'

    # sample standardization info
    # paste data from csv here (in between '''  ''')
    input_data = '''
    source_slot,source_well,dest_slot,dest_well,vol_dna,vol_water
    3,A1,5,A1,18.25,70.65
    3,A2,5,A2,88.9,0
    3,A3,5,A3,36.8,52.1
    3,A4,5,A4,88.9,0
    3,A5,5,A5,81.77,7.13
    3,A6,5,A6,88.9,0
    3,A7,5,A7,54.27,34.63
    3,A8,5,A8,75.7,13.2
    3,A9,5,A9,88.9,0
    1,A10,5,A10,50.75,38.15
    3,A10,5,A11,51.63,37.27
    3,A11,5,A12,47.74,41.16
    3,A12,5,B1,68.26,20.64
    3,B1,5,B2,31.55,57.35
    3,B2,5,B3,88.9,0
    3,B3,5,B4,64.83,24.07
    3,B4,5,B5,24.06,64.84
    3,B5,5,B6,51.82,37.08
    3,B6,5,B7,63.52,25.38
    3,B7,5,B8,62.58,26.32
    3,B8,5,B9,43.51,45.39
    3,B9,5,B10,60.17,28.73
    3,B10,5,B11,75.17,13.73
    3,B11,5,B12,31.04,57.86
    1,C1,5,C1,69.97,18.93
    3,B12,5,C2,15.09,73.81
    1,C3,5,C3,48.48,40.42
    3,C1,5,C4,53.11,35.79
    3,C2,5,C5,35.45,53.45
    3,C3,5,C6,68.91,19.99
    3,C4,5,C7,24.35,64.55
    3,C5,5,C8,88.9,0
    1,C9,5,C9,65.56,23.34
    3,C6,5,C10,67.95,20.95
    1,C11,5,C11,69.1,19.8
    3,C7,5,C12,30.18,58.72
    3,C8,5,D1,28.38,60.52
    3,C9,5,D2,24.91,63.99
    3,C10,5,D3,88.9,0
    3,C11,5,D4,42.72,46.18
    1,D5,5,D5,59.98,28.92
    1,D6,5,D6,37.61,51.29
    1,D7,5,D7,43.82,45.08
    1,D8,5,D8,25.78,63.12
    1,D9,5,D9,24.69,64.21
    1,D10,5,D10,51.25,37.65
    3,C12,5,D11,88.9,0
    3,D1,5,D12,29.27,59.63
    3,D2,5,E1,29.47,59.43
    1,E2,5,E2,68.62,20.28
    3,D3,5,E3,13.59,75.31
    3,D4,5,E4,22.04,66.86
    3,D5,5,E5,14.49,74.41
    3,D6,5,E6,19.01,69.89
    1,E7,5,E7,36.1,52.8
    1,E8,5,E8,37.74,51.16
    3,D7,5,E9,20.57,68.33
    1,E10,5,E10,48.77,40.13
    3,D8,5,E11,18.86,70.04
    3,D9,5,E12,25.95,62.95
    3,D10,5,F1,15.29,73.61
    3,D11,5,F2,21.48,67.42
    3,D12,5,F3,38.64,50.26
    1,F4,5,F4,76.22,12.68
    3,E1,5,F5,40.65,48.25
    3,E2,5,F6,32.3,56.6
    3,E3,5,F7,23.33,65.57
    3,E4,5,F8,25.04,63.86
    3,E5,5,F9,21.27,67.63
    3,E6,5,F10,36.11,52.79
    3,E7,5,F11,35.84,53.06
    3,E8,5,F12,38.68,50.22
    3,E9,5,G1,21.21,67.69
    3,E10,5,G2,40.8,48.1
    3,E11,5,G3,27.18,61.72
    3,E12,5,G4,26.56,62.34
    3,F1,5,G5,88.9,0
    3,F2,5,G6,29.35,59.55
    3,F3,5,G7,21.61,67.29
    3,F4,5,G8,34.95,53.95
    3,F5,5,G9,40.85,48.05
    3,F6,5,G10,51.82,37.08
    3,F7,5,G11,24.8,64.1
    3,F8,5,G12,43,45.9
    3,F9,5,H1,42.92,45.98
    3,F10,5,H2,40.71,48.19
    3,F11,5,H3,70.9,18
    3,F12,5,H4,54.48,34.42
    3,G1,5,H5,88.9,0
    1,H6,5,H6,70.75,18.15
    1,H7,5,H7,88.9,0
    1,H8,5,H8,88.9,0
    3,G2,6,A1,88.9,0
    3,G3,6,A2,88.9,0
    3,G4,6,A3,43.63,45.27
    3,G5,6,A4,88.9,0
    3,G6,6,A5,73.99,14.91
    2,A6,6,A6,52.83,36.07
    3,G7,6,A7,26.95,61.95
    3,G8,6,A8,33.32,55.58
    2,A9,6,A9,66.3,22.6
    2,A10,6,A10,52.08,36.82
    2,A11,6,A11,56.88,32.02
    2,A12,6,A12,52.79,36.11
    3,G9,6,B1,81.82,7.08
    2,B2,6,B2,62.57,26.33
    2,B3,6,B3,54.2,34.7
    2,B4,6,B4,44.37,44.53
    2,B5,6,B5,45.23,43.67
    2,B6,6,B6,61.5,27.4
    2,B7,6,B7,44.6,44.3
    2,B8,6,B8,45.88,43.02
    2,B9,6,B9,87.18,1.72
    2,B10,6,B10,80.14,8.76
    2,B11,6,B11,54.12,34.78
    2,B12,6,B12,64.27,24.63
    2,C1,6,C1,41.87,47.03
    2,C2,6,C2,27.49,61.41
    2,C3,6,C3,88.9,0
    2,C4,6,C4,61.79,27.11
    2,C5,6,C5,79.57,9.33
    2,C6,6,C6,52.03,36.87
    2,C7,6,C7,42.12,46.78
    2,C8,6,C8,57.29,31.61
    2,C9,6,C9,50.82,38.08
    2,C10,6,C10,75.73,13.17
    2,C11,6,C11,88.9,0
    2,C12,6,C12,88.9,0
    2,D1,6,D1,42.94,45.96
    2,D2,6,D2,39.42,49.48
    2,D3,6,D3,51.92,36.98
    2,D4,6,D4,88.9,0
    2,D5,6,D5,81.97,6.93
    2,D6,6,D6,70.42,18.48
    2,D7,6,D7,61.73,27.17
    2,D8,6,D8,54.95,33.95
    2,D9,6,D9,49.5,39.4
    2,D10,6,D10,45.05,43.85
    2,D11,6,D11,41.32,47.58
    2,D12,6,D12,38.17,50.73
    2,E1,6,E1,35.46,53.44
    3,H4,6,E2,52.27,36.63
    2,E3,6,E3,45.01,43.89
    3,H5,6,E4,35.52,53.38
    2,E5,6,E5,51.5,37.4
    2,E6,6,E6,39.56,49.34
    2,E7,6,E7,35.87,53.03
    2,E8,6,E8,65.36,23.54
    2,E9,6,E9,31.72,57.18
    2,E10,6,E10,56.19,32.71
    2,E11,6,E11,86.27,2.63
    2,E12,6,E12,73.13,15.77
    2,F1,6,F1,13.93,74.97
    2,F2,6,F2,77.39,11.51
    2,F3,6,F3,36.84,52.06
    2,F4,6,F4,47.19,41.71
    2,F5,6,F5,34.28,54.62
    2,F6,6,F6,34.6,54.3
    2,F7,6,F7,46.12,42.78
    2,F8,6,F8,50.42,38.48
    2,F9,6,F9,64.44,24.46
    3,F10,6,F10,88.9,0
    2,F11,6,F11,60.14,28.76
    2,F12,6,F12,36.56,52.34
    '''

    ########## DO NOT EDIT BELOW THIS LINE ##########

    # turn on lights if not on already
    protocol.set_rail_lights(True)

    # checks
    if pipette_mount_300 == pipette_mount_20:
        raise Exception('Invalid pipette placement')
    if pipette_mount_300 is None:
        raise Exception('Must attach single channel p300')
    if pipette_mount_20 is None:
        raise Exception("Must attach single channel p20")
    if num_source_plates < 1 or num_source_plates > 3:
        raise Exception("Invalid number of source plates. Must be 1-3")
    if num_destination_plates < 1 or num_destination_plates > 2:
        raise Exception("Invalid number of destination plates. Must be 1-2")

    # Define hardware, pipettes/tips, plates
    # load tips
    if extra_rack_type == '300':
        tips300 = [protocol.load_labware(
            'opentrons_96_tiprack_300ul', str(slot)) for slot in [
            7, 10, 11]]
        tips20 = [protocol.load_labware(
            'opentrons_96_filtertiprack_20ul', str(slot)) for slot in [
            8, 9]]
    elif extra_rack_type == '20':
        tips300 = [protocol.load_labware(
            'opentrons_96_tiprack_300ul', str(slot)) for slot in [
            10, 11]]
        tips20 = [protocol.load_labware(
            'opentrons_96_filtertiprack_20ul', str(slot)) for slot in [
            7, 8, 9]]
    elif extra_rack_type == 'none':
        tips300 = [protocol.load_labware(
            'opentrons_96_tiprack_300ul', str(slot)) for slot in [
            10, 11]]
        tips20 = [protocol.load_labware(
            'opentrons_96_filtertiprack_20ul', str(slot)) for slot in [
            8, 9]]
    else:
        raise Exception("Extra tip rack type not specified. Must be '20', '300', or 'none'")

    # specify pipette, mount location, and tips
    p300 = protocol.load_instrument("p300_single_gen2", mount=pipette_mount_300, tip_racks=tips300)
    p20 = protocol.load_instrument("p20_single_gen2", mount=pipette_mount_20, tip_racks=tips20)

    # load reagent labware and specify reagents in each well/columns
    water_reservoir = protocol.load_labware(
        'nest_12_reservoir_15ml', '4')
    water = [water_reservoir.wells_by_name()[well] for well in ['A1']]

    # load plates
    # add first source DNA plate
    if source_plate_type == 'nest_100ul':
        protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '1', 'DNA source plate 1')
    elif source_plate_type == 'biorad_200ul':
        protocol.load_labware('biorad_96_wellplate_200ul_pcr', '1', 'DNA source plate 1')
    else:
        raise Exception("Invalid source plate type")
    # if more than one plate, add 2nd
    if num_source_plates > 1:
        if source_plate_type == 'nest_100ul':
            protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '2', 'DNA source plate 2')
        elif source_plate_type == 'biorad_200ul':
            protocol.load_labware('biorad_96_wellplate_200ul_pcr', '2', 'DNA source plate 2')
        else:
            raise Exception('Invalid source plate type')
    # if more than 2 plates, add 3rd
    if num_source_plates > 2:
        if source_plate_type == 'nest_100ul':
            protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '3', 'DNA source plate 3')
        elif source_plate_type == 'biorad_200ul':
            protocol.load_labware('biorad_96_wellplate_200ul_pcr', '3', 'DNA source plate 3')
        else:
            raise Exception('Invalid source plate type')
    # add first DNA destination plate
    if destination_plate_type == 'nest_100ul':
        protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '5', 'DNA destination plate 1')
    elif destination_plate_type == 'biorad_200ul':
        protocol.load_labware('biorad_96_wellplate_200ul_pcr', '5', 'DNA destination plate 1')
    else:
        raise Exception('Invalid destination plate type')
    # if more than one plate, add second
    if num_destination_plates > 1:
        if destination_plate_type == 'biorad_200ul':
            protocol.load_labware('biorad_96_wellplate_200ul_pcr', '6', 'DNA destination plate 2')
        elif destination_plate_type == 'nest_100ul':
            protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '6', 'DNA destination plate 2')
        else:
            raise Exception('Invalid destination plate type')

    # parse input data
    csv_data = [[val.strip() for val in line.split(',')]
                for line in input_data.splitlines()
                if line.split(',')[0].strip()][1:]

    # set aspirate and dispense speeds
    # smaller volumes need to be dispnensed slower than larger volumes
    p20.flow_rate.aspirate = 150
    p20.flow_rate.dispense = 150
    p300.flow_rate.aspirate = 150
    p300.flow_rate.dispense = 150

    # add water to destination wells
    # p300 will use the same tip for all wells
    # p20 will change tip in between each sample depending on whether or not the destination plate is clean
    # pickup tip for p300
    p300.pick_up_tip()
    # pickup tip for p20 if using the same one for this step
    if destination_plate_status == 'clean':
        p20.pick_up_tip()
    # loop through wells and add water
    for row in csv_data:
        dest_well = protocol.loaded_labwares[int(row[2])].wells_by_name()[row[3]]
        vol_water = float(row[5])
        # check volume
        if vol_water < 0.0 or vol_water > 200.0:
            raise Exception("Invalid volume of water. Must be between 0.0-200.0")
        # round to 2 decimal places
        vol_water = round(vol_water, 2)
        # use p20 if between 1-20
        # water tends to cling to tip at vol <20 so a touch-tip step is included
        if 0 < vol_water <= 20:
            # if plate previously held DNA, change tip everytime
            if destination_plate_status == 'used':
                p20.transfer(vol_water, water, dest_well.top(1), blow_out=True,
                             blowout_location='destination well', touch_tip=True, new_tip='always')
            elif destination_plate_status == 'clean':
                # don't change tips if it's a clean plate
                p20.transfer(vol_water, water, dest_well.top(1), blow_out=True,
                             blowout_location='destination well', touch_tip=True, new_tip='never')
            else:
                raise Exception("Destination plate status not indicated. Must be 'clean' or 'used'.")
        # use p300 if >20 and dispense at top of well so nothing touches and you can ues the same tip
        if vol_water > 20:
            p300.transfer(vol_water, water, dest_well.top(1), blow_out=True,
                          blowout_location='destination well', new_tip='never')
    # drop tips after all water is added
    p300.drop_tip()
    if destination_plate_status == 'clean':
        p20.drop_tip()

    # add dna to each well
    for row in csv_data:
        source_well = protocol.loaded_labwares[int(row[0])].wells_by_name()[row[1]]
        dest_well = protocol.loaded_labwares[int(row[2])].wells_by_name()[row[3]]
        vol_dna = float(row[4])
        # check volume
        if vol_dna < 1.0 or vol_dna > 200.0:
            raise Exception("Invalid volume of dna. Must be between 1.0-200.0")
        # round to 2 decimal places
        vol_dna = round(vol_dna, 2)
        # use p20 if appropriate volume
        if 0 < vol_dna <= 20:
            p20.transfer(vol_dna, source_well, dest_well, blow_out=True,
                         blowout_location='destination well', touch_tip=True, new_tip='always')
        # use p300 if appropriate volume
        if vol_dna > 20:
            p300.transfer(vol_dna, source_well, dest_well, blow_out=True,
                          blowout_location='destination well', touch_tip=True, new_tip='always')

    # turn off lights
    protocol.set_rail_lights(False)
