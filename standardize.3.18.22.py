import csv

metadata = {
    'protocolName': 'Standardize DNA Concentrations',
    'author': 'AMB, last updated 3/23/22',
    'description': 'Adds designated amounts of DNA and water to wells in order to '
                   'standardize samples to a target concentration',
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

    # sample standardization info
    # paste data from csv here (in between '''  ''')
    input_data = '''
    source_slot,source_well,dest_slot,dest_well,vol_dna,vol_water
    1,A1,5,A1,40,60
    1,C1,5,A2,66.67,19.5
    1,D1,5,A3,20,80
    2,E3,5,B4,10.2,90
    2,A12,5,B5,45.9,43.0
    2,B5,5,B6,87.2,1.7
    2,H8,5,D11,80.1,8.8
    3,C11,5,H12,54.1,34.8
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
    tips300 = [
     protocol.load_labware(
      'opentrons_96_tiprack_300ul', str(slot)) for slot in [
      7, 10, 11]]
    tips20 = [
     protocol.load_labware(
      'opentrons_96_filtertiprack_20ul', str(slot)) for slot in [
      8, 9]]
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
        protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '1')
    elif source_plate_type == 'biorad_200ul':
        protocol.load_labware('biorad_96_wellplate_200ul_pcr', '1')
    else:
        raise Exception("Invalid source plate type")
    #if more than one plate, add 2nd
    if num_source_plates > 1:
        if source_plate_type == 'nest_100ul':
            protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '2')
        elif source_plate_type == 'biorad_200ul':
            protocol.load_labware('biorad_96_wellplate_200ul_pcr', '2')
        else:
            raise Exception('Invalid source plate type')
    # if more than 2 plates, add 3rd
    if num_source_plates > 2:
        if source_plate_type == 'nest_100ul':
            protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '3')
        elif source_plate_type == 'biorad_200ul':
            protocol.load_labware('biorad_96_wellplate_200ul_pcr', '3')
        else:
            raise Exception('Invalid source plate type')
    # add first DNA destination plate
    if destination_plate_type == 'nest_100ul':
        protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt','5')
    elif destination_plate_type == 'biorad_200ul':
        protocol.load_labware('biorad_96_wellplate_200ul_pcr', '5')
    else:
        raise Exception('Invalid destination plate type')
    # if more than one plate, add second
    if num_destination_plates > 1:
        if destination_plate_type == 'biorad_200ul':
            protocol.load_labware('biorad_96_wellplate_200ul_pcr', '6')
        elif destination_plate_type == 'nest_100ul':
            protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '6')
        else:
            raise Exception('Invalid destination plate type')

    # parse input data
    csv_data = [[val.strip() for val in line.split(',')]
                for line in input_data.splitlines()
                if line.split(',')[0].strip()][1:]

    # set aspirate and dispense speeds
    p20.flow_rate.aspirate = 150
    p20.flow_rate.dispense = 150
    p300.flow_rate.aspirate = 150
    p300.flow_rate.dispense = 150

    # add water to all destination wells
    # first have both pipettes pick up tips
    p20.pick_up_tip()
    p300.pick_up_tip()
    # loops through wells and add water
    for row in csv_data:
        dest_well = protocol.loaded_labwares[int(row[2])].wells_by_name()[row[3]]
        vol_water = float(row[5])
        # check volume
        if vol_water < 1.0 or vol_water > 200.0:
            raise Exception("Invalid volume of water. Must be between 1.0-200.0")
        # round to 2 decimal places
        vol_water = round(vol_water, 2)
        # use p20 if appropriate volume. Dispense at top of well so nothing touches and you can ues the same tip
        if 0 < vol_water <= 20:
            p20.transfer(vol_water, water, dest_well.top(1), blow_out=True,
                        blowout_location='destination well', new_tip='never')
        # use p300 if appropriate volume. Dispense at top of well so nothing touches and you can ues the same tip
        if vol_water > 20:
            p300.transfer(vol_water, water, dest_well.top(1), blow_out=True,
                        blowout_location='destination well', new_tip='never')
    # drop tips after all water has been added
    p20.drop_tip()
    p300.drop_tip()

    # add dna to each well
    for row in csv_data:
        source_well = protocol.loaded_labwares[int(row[0])].wells_by_name()[row[1]]
        dest_well = protocol.loaded_labwares[int(row[2])].wells_by_name()[row[3]]
        vol_dna = float(row[4])
        # check volume
        if vol_dna < 1.0 or vol_dna > 200.0:
            raise Exception("Invalid volume of water. Must be between 1.0-200.0")
        # round to 2 decimal places
        vol_dna = round(vol_dna,2)
        # use p20 if appropriate volume
        if 0 < vol_dna <= 20:
            p20.transfer(vol_dna, source_well, dest_well, blow_out=True,
                        blowout_location='destination well', new_tip='always')
        # use p300 if appropriate volume
        if vol_dna > 20:
            p300.transfer(vol_dna, source_well, dest_well, blow_out=True,
                        blowout_location='destination well', new_tip='always')

    # turn off lights
    protocol.set_rail_lights(False)
