metadata = {
    'protocolName': 'Standardize DNA Concentrations',
    'author': 'AMB, last updated 4/18/22',
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

    # source plate 1 type ('biorad_200ul' or 'nest_100ul', all lowercase and in single quotes)
    source_p1 = 'nest_100ul'

    # source plate 2 type ('biorad_200ul', 'nest_100ul', or 'none', all lowercase and in single quotes)
    source_p2 = 'none'

    # source plate 3 type ('biorad_200ul', 'nest_100ul', or 'none', all lowercase and in single quotes)
    source_p3 = 'none'

    # destination plate 1 type ('biorad_200ul' or 'nest_100ul', all lowercase and in single quotes)
    destination_p1 = 'biorad_200ul'

    # destination plate 2 type ('biorad_200ul', 'nest_100ul', or 'none', all lowercase and in single quotes)
    destination_p2 = 'none'

    # pre-used or fresh destination plate ('used' or 'clean', all lowercase and in single quotes)
    destination_plate_status = 'used'

    # 3rd tip rack type ('20','300', or 'none',  in single quotes)
    extra_rack_type = 'none'

    # sample standardization info
    # paste data from csv here (in between '''  ''')
    input_data = '''
    source_slot,source_well,dest_slot,dest_well,vol_dna,vol_water
    1,A1,5,A1,40,60
    1,C1,5,B1,66.67,19.5
    1,D1,5,C1,20,80
    2,E3,5,D1,10.2,90
    2,A12,6,A1,45.9,43.0
    2,B5,6,B1,87.2,1.7
    2,H8,6,C1,80.1,8.8
    3,C11,6,D1,54.1,34.8
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

    # Define hardware, pipettes/tips, plates
    # load tips
    if extra_rack_type == '300':
        tips300 = [protocol.load_labware(
            'opentrons_96_tiprack_300ul', str(slot)) for slot in [
            7, 10, 11]]
        tips20 = [protocol.load_labware(
            'opentrons_96_tiprack_20ul', str(slot)) for slot in [
            8, 9]]
    elif extra_rack_type == '20':
        tips300 = [protocol.load_labware(
            'opentrons_96_tiprack_300ul', str(slot)) for slot in [
            10, 11]]
        tips20 = [protocol.load_labware(
            'opentrons_96_tiprack_20ul', str(slot)) for slot in [
            7, 8, 9]]
    elif extra_rack_type == 'none':
        tips300 = [protocol.load_labware(
            'opentrons_96_tiprack_300ul', str(slot)) for slot in [
            10, 11]]
        tips20 = [protocol.load_labware(
            'opentrons_96_tiprack_20ul', str(slot)) for slot in [
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
    if source_p1 == 'nest_100ul':
        protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '1', 'DNA source plate 1')
    elif source_p1 == 'biorad_200ul':
        protocol.load_labware('biorad_96_wellplate_200ul_pcr', '1', 'DNA source plate 1')
    else:
        raise Exception("Invalid source plate type")
    # add 2nd source plate
    if source_p2 == 'nest_100ul':
        protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '2', 'DNA source plate 2')
    elif source_p2 == 'biorad_200ul':
        protocol.load_labware('biorad_96_wellplate_200ul_pcr', '2', 'DNA source plate 2')
    elif source_p2 == 'none':
        pass
    else:
        raise Exception('Invalid source plate type')
    # add 3rd source plate
    if source_p3 == 'nest_100ul':
        protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '3', 'DNA source plate 3')
    elif source_p3 == 'biorad_200ul':
        protocol.load_labware('biorad_96_wellplate_200ul_pcr', '3', 'DNA source plate 3')
    elif source_p3 == 'none':
        pass
    else:
        raise Exception('Invalid source plate type')

    # add first DNA destination plate
    if destination_p1 == 'nest_100ul':
        protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '5', 'DNA destination plate 1')
    elif destination_p1 == 'biorad_200ul':
        protocol.load_labware('biorad_96_wellplate_200ul_pcr', '5', 'DNA destination plate 1')
    else:
        raise Exception('Invalid destination plate type')
    # add 2nd destination plate
    if destination_p2 == 'biorad_200ul':
        protocol.load_labware('biorad_96_wellplate_200ul_pcr', '6', 'DNA destination plate 2')
    elif destination_p2 == 'nest_100ul':
        protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '6', 'DNA destination plate 2')
    elif destination_p2 == 'none':
        pass
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
