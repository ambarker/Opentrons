metadata = {
    'protocolName': 'Ligation prep',
    'author': 'AMB, last updated 5/6/22',
    'description': 'Distribute ligation master mix into plates and add barcodes.',
    'apiLevel': '2.11'
}


def run(protocol):
    ########## EDIT THESE RUN OPTIONS AS NEEDED ##########

    # location of p20 single channel ('left' or 'right', all lowercase and in single quotes)
    pipette_mount_20 = 'right'

    # number of sample plates (integar, max:2)
    sample_plates = 2

    # number of samples in each plate (list of integers, surrounded by brackets and separated by commas)
    # ex: [96, 12, 72]
    # (will go by rows, i.e. 12 would mean samples A1-A12, 30 would mean A1-C6)
    num_samples_each_plate = [24, 12]

    # list wells that should be skipped (well name in single quotes and in brackets. Multiple wells separated by commas
    # ex: ['C2', 'D11', 'E1']
    # these samples should be included in the sample count above
    # ex: you want the protocol to distribute all the way to A12, but skip A10
    # your sample count would be 12 and then you would indicate to skip A10: P1_skip = ['A10']
    # if not skipping anything or not using that plate don't put anything between brackets
    P1_skip = ['A1', 'A11']
    P2_skip = []

    # sample plate type ('biorad_200ul' or 'nest_100ul', all lowercase and in single quotes)
    plate_type = 'biorad_200ul'

    # volume (ul) of master mix to add to each well (must be 1-20 ul)
    mm_vol = 7

    # volume (ul) of P1 adapter (barcodes) to add
    P1_vol = 2.0

    barcode_data = '''
    barcode_well, dest_slot, dest_well
    A1,5,A1
    A2,5,A2
    A3,5,A3
    A4,5,A4
    A1,6,A1
    A2,6,A2
    A3,6,A3
    '''

    ########## DO NOT EDIT BELOW THIS LINE ##########

    # turn on lights if not on already
    protocol.set_rail_lights(True)

    # checks
    if len(num_samples_each_plate) != sample_plates:
        raise Exception("The number of sample plates does not match the number of samples for each plate.")

    # Define hardware
    # load tip racks
    tips20 = [protocol.load_labware(
        'opentrons_96_tiprack_20ul', str(slot)) for slot in [7, 8, 9, 10]]

    # specify pipette, mount location, and tips
    p20 = protocol.load_instrument("p20_single_gen2", mount=pipette_mount_20, tip_racks=tips20)

    # load plates
    plate_names = []
    # add first sample plate
    if plate_type == 'nest_100ul':
        plate_1 = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '5', 'sample plate 1')
        plate_names.append(plate_1)
    elif plate_type == 'biorad_200ul':
        plate_1 = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '5', 'sample plate 1')
        plate_names.append(plate_1)
    else:
        raise Exception('Invalid destination plate type')
    # add 2nd destination plate
    if sample_plates == 2:
        if plate_type == 'biorad_200ul':
            plate_2 = protocol.load_labware('biorad_96_wellplate_200ul_pcr', '6', 'sample plate 2')
            plate_names.append(plate_2)
        elif plate_type == 'nest_100ul':
            plate_2 = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '6', 'sample plate 2')
            plate_names.append(plate_2)
        else:
            raise Exception('Invalid destination plate type')

    # load temperature module, tube rack, and mater mix
    temp_mod = protocol.load_module('temperature module gen2', '1')
    temp_mod.set_temperature(4)  # set temp block temperature
    tube_rack = temp_mod.load_labware('opentrons_24_aluminumblock_nest_1.5ml_snapcap', 'master mix tube')
    mm_tube = tube_rack.wells_by_name()['A1']

    # load P1 adapters
    adapter_plate = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul', '2',
                                         'P1 adapter strip tubes')

    # set aspirate and dispense speeds
    p20.flow_rate.aspirate = 150
    p20.flow_rate.dispense = 150

    # parse input data
    csv_data = [[val.strip() for val in line.split(',')]
                for line in barcode_data.splitlines()
                if line.split(',')[0].strip()][1:]

    # list of possible wells
    well_names = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12',
                  'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12',
                  'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12',
                  'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12',
                  'E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'E10', 'E11', 'E12',
                  'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
                  'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10', 'G11', 'G12',
                  'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'H11', 'H12']

    # add barcodes
    for row in csv_data:
        source_well = adapter_plate.wells_by_name()[row[0]]
        dest_well = protocol.loaded_labwares[int(row[1])].wells_by_name()[row[2]]
        p20.pick_up_tip()
        p20.aspirate(P1_vol, source_well)
        p20.touch_tip()
        p20.dispense(P1_vol, dest_well.bottom())
        p20.move_to(dest_well.top())
        p20.blow_out()
        p20.touch_tip()
        p20.drop_tip()

    # distribute master mix
    # list of wells to skip for each plate
    wells_skip = [P1_skip, P2_skip]

    for num_plate in range(0, len(plate_names)):
        for sample in range(0, num_samples_each_plate[num_plate]):
            plate = plate_names[num_plate]
            sample_name = well_names[sample]
            # move on to next iteration of loop if sample name is in the skip list for this plate
            if sample_name in wells_skip[num_plate]:
                continue
            p20.pick_up_tip()
            p20.aspirate(mm_vol, mm_tube)
            p20.dispense(mm_vol, plate.wells_by_name()[sample_name].top())
            p20.blow_out()
            #p20.touch_tip()
            p20.drop_tip()

    # turn off lights when protocol complete
    protocol.set_rail_lights(False)


