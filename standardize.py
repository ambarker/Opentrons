metadata = {
    'protocolName': 'Standardize DNA Concentrations',
    'author': 'AMB, last updated 5/6/22',
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
    source_p2 = 'nest_100ul'

    # source plate 3 type ('biorad_200ul', 'nest_100ul', or 'none', all lowercase and in single quotes)
    source_p3 = 'nest_100ul'

    # destination plate 1 type ('biorad_200ul' or 'nest_100ul', all lowercase and in single quotes)
    destination_p1 = 'biorad_200ul'

    # destination plate 2 type ('biorad_200ul', 'nest_100ul', or 'none', all lowercase and in single quotes)
    destination_p2 = 'biorad_200ul'

    # pre-used or fresh destination plate ('used' or 'clean', all lowercase and in single quotes)
    destination_plate_status = 'clean'

    # 3rd tip rack type ('20','300', or 'none',  in single quotes)
    extra_rack_type = 'none'

    # sample standardization info
    # paste data from csv here (in between '''  ''')
    input_data = '''
    source_slot,source_well,dest_slot,dest_well,vol_dna,vol_water
    1,A1,5,A1,40,60
    1,A2,5,A2,66.67,19.5
    1,A3,5,A3,20,80
    1,A5,5,A4,10.2,90
    1,A8,5,A5,45.9,43.0
    1,A12,5,A6,87.2,1.7
    2,A1,5,A7,80.1,8.8
    2,A2,5,A8,15.2,5
    2,A5,6,A1,2,2
    2,A6,6,A2,67,1
    2,A8,6,A3,5,10 
    3,A5,6,D1,54.1,34.8
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
    water_reservoir = protocol.load_labware('nest_12_reservoir_15ml', '4')

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
    p20.flow_rate.aspirate = 150
    p20.flow_rate.dispense = 150
    p300.flow_rate.aspirate = 150
    p300.flow_rate.dispense = 150

    # add water to destination wells
    # if clean p300 and p20  will use the same tip for all wells
    # if not,p20 will change tip in between each sample if dispensed vol is <10 ul
    if destination_plate_status == "clean":
        # pick up tips that will be used the whole time
        p20.pick_up_tip()
        p300.pick_up_tip()
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
            # water tends to cling to tip at vol <10 so a touch-tip step is included
            if 0 < vol_water <= 20:
                p20.aspirate(vol_water, water_reservoir.wells()[0])
                p20.dispense(vol_water, dest_well.top())
                p20.blow_out()
                if vol_water < 10:
                    p20.touch_tip()
            if vol_water > 20:
                p300.aspirate(vol_water, water_reservoir.wells()[0])
                p300.dispense(vol_water, dest_well.top())
                p300.blow_out()
        p20.drop_tip()
        p300.drop_tip()
    elif destination_plate_status == "used":
        # pick up tips
        p20.pick_up_tip()
        p300.pick_up_tip()
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
            # water tends to cling to tip at vol <10 so a touch-tip step is included
            if 0 < vol_water <= 20:
                p20.aspirate(vol_water, water_reservoir.wells()[0])
                p20.dispense(vol_water, dest_well.top())
                p20.blow_out()
                if vol_water < 10:
                    p20.touch_tip()
                    p20.drop_tip()
                    p20.pick_up_tip()
            if vol_water > 20:
                p300.aspirate(vol_water,  water_reservoir.wells()[0])
                p300.dispense(vol_water, dest_well.top())
                p300.blow_out()
        p20.drop_tip()
        p300.drop_tip()
    else:
        raise Exception("Destination plate status not indicated. Must be 'clean' or 'used'.")


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
            p20.pick_up_tip()
            p20.aspirate(vol_dna, source_well)
            p20.touch_tip()
            p20.dispense(vol_dna, dest_well)
            p20.blow_out()
            p20.touch_tip()
            p20.drop_tip()
        # use p300 if appropriate volume
        if vol_dna > 20:
            p300.pick_up_tip()
            p300.aspirate(vol_dna, source_well)
            p300.touch_tip()
            p300.dispense(vol_dna, dest_well)
            p300.blow_out()
            p300.touch_tip()
            p300.drop_tip()

    # turn off lights
    protocol.set_rail_lights(False)
