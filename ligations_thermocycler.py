metadata = {
    'protocolName': 'Distribute master mix into sample plates',
    'author': 'AMB, last updated 3/28/22',
    'description': 'Generic protocol to distribute master mix from 2 mL tube to PCR plates.',
    'apiLevel': '2.11'
}


def run(protocol):
    ########## EDIT THESE RUN OPTIONS AS NEEDED ##########

    # location of p20 single channel ('left' or 'right', all lowercase and in single quotes)
    pipette_mount_20 = 'right'

    # number of samples (integar, max 96)
    # (will go by rows, i.e. 12 would mean samples A1-A12)
    num_samples = 96

    # list wells that should be skipped (well name in single quotes and in brackets. Multiple wells separated by commas
    # ex: ['C2', 'D11', 'E1']
    # these samples should be included in the sample count above
    # ex: you want the protocol to distribute all the say to A12, but skip A10
    # you sample count would be 12 and then you would indicate to skip A10: well_skip = [`A10']
    # if nothing than don't put anything between brackets
    well_skip = ['A1', 'A2']

    # sample plate type ('biorad_200ul' or 'nest_100ul', all lowercase and in single quotes)
    plate_type = 'biorad_200ul'

    # volume (ul) of master mix to add to each well (must be 1-20 ul)
    mm_vol = 11.1

    # mix after pipetting master mix into sample ('yes' or 'no', all lowercase and in single quotes)
    mix_sample = 'no'

    barcode_data = '''
    barcode_well,sample_well
    A1,A1
    A2,A2
    A3,A3
    A4,A4
    '''

    ########## DO NOT EDIT BELOW THIS LINE ##########

    # turn on lights if not on already
    protocol.set_rail_lights(True)

    # Define hardware
    # load thermocycler module & sample plate
    thermo_mod = protocol.load_module('thermocycler module')
    if plate_type == 'biorad_200ul':
        thermo_plate = thermo_mod.load_labware('biorad_96_wellplate_200ul_pcr')
    elif plate_type == 'nest_100ul':
        thermo_plate = thermo_mod.load_labware('nest_96_wellplate_100ul_pcr_full_skirt')
    else:
        raise Exception("Invalid sample plate type")

    # load temperature module, tube rack, and mater mix
    temp_mod = protocol.load_module('temperature module gen 2', '1')
    temp_tube_rack = temp_mod.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap')
    mm_tube = temp_tube_rack.wells_by_name()['A1']

    # load P1 adapters
    adapter_plate = protocol.load_module('opentrons_96_aluminumblock_generic_pcr_strip_200ul', '2',
                                         'P1 adapter strip tubes')


    # load pipette and tips
    tips20 = [protocol.load_labware(
        'opentrons_96_filtertiprack_20ul', str(slot)) for slot in [
        3, 4]]
    p20 = protocol.load_instrument("p20_single_gen2", mount=pipette_mount_20, tip_racks=tips20)

    # set aspirate and dispense speeds
    p20.flow_rate.aspirate = 150
    p20.flow_rate.dispense = 150



    # list of possible wells
    well_names = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12',
                  'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12',
                  'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12',
                  'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12',
                  'E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'E10', 'E11', 'E12',
                  'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
                  'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10', 'G11', 'G12',
                  'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'H11', 'H12']

    # list of wells to skip for each plate
    wells_skip = [P1_skip, P2_skip, P3_skip, P4_skip, P5_skip]

    # distribute master mix
    for num_plate in range(0, len(plate_names)):
        for sample in range(0, num_samples_each_plate[num_plate]):
            plate = plate_names[num_plate]
            sample_name = well_names[sample]
            # move on to next iteration of loop if sample name is in the skip list for this plate
            if sample_name in wells_skip[num_plate]:
                continue
            if mix_sample == 'yes':
                p20.transfer(mm_vol, mm_tube, plate.wells_by_name()[sample_name], mix_after=(3, mm_vol),
                             blow_out=True, blowout_location='destination well', touch_tip=True, new_tip='always')
            elif mix_sample == 'no':
                p20.transfer(mm_vol, mm_tube, plate.wells_by_name()[sample_name],
                             blow_out=True, blowout_location='destination well', touch_tip=True, new_tip='always')
            else:
                raise Exception('Must indicate if sample should be mixed after adding master mix')


    # turn off lights when protocol compelte
    protocol.set_rail_lights(False)