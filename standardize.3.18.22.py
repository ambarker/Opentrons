metadata = {
    'protocolName': 'Standardize DNA Concentrations',
    'author': 'AMB, last updated 3/21/22',
    'description': 'Add designated amounts of DNA and water to standardize samples to a target concentration',
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

    # sample standardization info




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
    # specify tips and slots
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

    # specify reagent labware, reagents in each well, and slot on deck
    water_reservoir = protocol.load_labware(
        'nest_12_reservoir_15ml', '4')
    [water] = [reagent_reservoir.wells_by_name()[well] for well in ['A1']]
    if num_source_plates == 1:
        dna_source_plate = [protocol.load_labware(
            'nest_96_wellplate_100ul_pcr_full_skirt',
            str(slot)) for slot in [1]]
    if num_source_plates == 2:
        dna_source_plate = [protocol.load_labware(
            'nest_96_wellplate_100ul_pcr_full_skirt',
            str(slot)) for slot in [1, 2]]
    if num_source_plates == 3:
        dna_source_plate = [protocol.load_labware(
            'nest_96_wellplate_100ul_pcr_full_skirt',
            str(slot)) for slot in [1, 2, 3]]
    if dna_destinatio_plate == 1:
        dna_destination_plate = [protocol.load_labware(
            'biorad_96_wellplate_200ul_pcr',
            str(slot)) for slot in [5]]
    if dna_destinatio_plate == 2:
        dna_destination_plate = [protocol.load_labware(
            'biorad_96_wellplate_200ul_pcr',
            str(slot)) for slot in [5, 6]]



    # Add ampure/PEG
    for index, column in enumerate(mag_plate.columns()[:num_cols]):
        ccst = capture_current_starting_tip()
        name_the_tips(ccst[0], ['sup_tips'], [
            named_tips['current_tip'].well_name])
        p300.pick_up_tip()
        # if adding beads, mix 2 times before pipetting
        p300.flow_rate.aspirate = 100
        p300.flow_rate.dispense = 100
        if beads_peg == 'beads':
            p300.mix(2, 150, beads.bottom(1))
        p300.flow_rate.aspirate = 50
        p300.flow_rate.dispense = 50
        # add specified volume of beads/PEG to samples
        p300.transfer(
         bead_volume, beads.bottom(1), column[0].bottom(3), new_tip='never')
        # pipette up and down 5 times
        p300.mix(5, bead_volume, column[0].bottom(2))
        p300.move_to(column[0].top())
        p300.blow_out()
        # touch pipette tip to side of wells to knock off any remaining liquid
        p300.touch_tip()
        p300.return_tip()

    # Incubate beads and DNA at RT
    msg = "Incubating the beads for "+str(incubation_time)+" minutes. \
    Protocol will resume automatically."
    protocol.delay(minutes=incubation_time, msg=msg)

    # Engage magdeck
    mag_deck.engage()
    protocol.comment("Delaying for "+str(settling_time)+" minutes for \
beads to settle. Protocol will resume automatically.")
    protocol.delay(minutes=settling_time)

    # Aspirate supernatant
    for index, column in enumerate(mag_plate.columns()[:num_cols]):
        p300.pick_up_tip(named_tips['sup_tips'][index])
        p300.move_to(column[0].top())
        # aspirate really slowly to limit amount of beads
        p300.flow_rate.aspirate = 5
        p300.flow_rate.dispense = 100
        # limits up/down movement speed of pipette
        protocol.max_speeds['Z'] = 10
        p300.aspirate(total_vol, column[0].bottom(1))
        p300.move_to(column[0].top())
        protocol.max_speeds['Z'] = None
        protocol.delay(seconds=1)
        # dispense in waste reservoir
        p300.dispense(total_vol, waste_reservoir.wells()[0].top())
        p300.blow_out(waste_reservoir.wells()[0].top())
        p300.return_tip()

    # EtOH wash 1
    # loop through groups
    for g in range(0, num_groups):
        p300.flow_rate.aspirate = 100
        p300.flow_rate.dispense = 150
        p300.pick_up_tip()
        # add ethanol to each column in current group
        for index, column in enumerate(mag_plate.columns()[grps[g][0]:grps[g][1]], grps[g][0]):
            p300.transfer(
                etoh_volume, etoh_1.bottom(1), column[0].top(-1), new_tip='never')
            p300.move_to(column[0].top())
            p300.blow_out()
            protocol.delay(seconds=1)
        p300.drop_tip()

        # Incubate etoh
        # if 3 columns in group, go straight to aspirate
        if grps[g][1]-grps[g][0] == 3:
            pass
        # if 1-2 columns, delay for appropriate amount of time
        elif grps[g][1] - grps[g][0] == 2:
            etoh_time = 5
            protocol.comment("Let ethanol sit for " + str(etoh_time) + " seconds. Protocol will resume automatically.")
            protocol.delay(seconds=etoh_time)
        elif grps[g][1] - grps[g][0] == 1:
            etoh_time = 8
            protocol.comment("Let ethanol sit for " + str(etoh_time) + " seconds. Protocol will resume automatically.")
            protocol.delay(seconds=etoh_time)

        # Aspirate etoh using parked tips
        for index, column in enumerate(mag_plate.columns()[grps[g][0]:grps[g][1]], grps[g][0]):
            p300.flow_rate.aspirate = 40
            p300.flow_rate.dispense = 150
            p300.pick_up_tip(named_tips['sup_tips'][index])
            p300.move_to(column[0].top())
            protocol.max_speeds['Z'] = 10
            p300.aspirate(etoh_volume, column[0].bottom(1))
            p300.move_to(column[0].top())
            protocol.max_speeds['Z'] = None
            protocol.delay(seconds=1)
            p300.air_gap(10)
            p300.dispense(etoh_volume + 10, waste_reservoir.wells()[0].top())
            p300.blow_out(waste_reservoir.wells()[0].top())
            p300.return_tip()

    # EtOH wash 2
    for g in range(0, num_groups):
        p300.flow_rate.aspirate = 100
        p300.flow_rate.dispense = 150
        p300.pick_up_tip()
        for index, column in enumerate(mag_plate.columns()[grps[g][0]:grps[g][1]], grps[g][0]):
            p300.transfer(
                etoh_volume, etoh_2.bottom(1), column[0].top(-1), new_tip='never')
            p300.move_to(column[0].top())
            p300.blow_out()
            protocol.delay(seconds=1)
        p300.drop_tip()

        # Incubate etoh
        # if 3 columns in group, go straight to aspirate
        if grps[g][1]-grps[g][0] == 3:
            pass
        # if 1-2 columns, delay for appropriate amount of time
        elif grps[g][1] - grps[g][0] == 2:
            etoh_time = 5
            protocol.comment("Let ethanol sit for " + str(etoh_time) + " seconds. Protocol will resume automatically.")
            protocol.delay(seconds=etoh_time)
        elif grps[g][1] - grps[g][0] == 1:
            etoh_time = 8
            protocol.comment("Let ethanol sit for " + str(etoh_time) + " seconds. Protocol will resume automatically.")
            protocol.delay(seconds=etoh_time)

        # Aspirate etoh
        for index, column in enumerate(mag_plate.columns()[grps[g][0]:grps[g][1]], grps[g][0]):
            p300.flow_rate.aspirate = 40
            p300.flow_rate.dispense = 150
            p300.pick_up_tip(named_tips['sup_tips'][index])
            p300.move_to(column[0].top())
            protocol.max_speeds['Z'] = 10
            p300.aspirate(etoh_volume, column[0].bottom(1))
            p300.move_to(column[0].top())
            protocol.max_speeds['Z'] = None
            protocol.delay(seconds=1)
            p300.air_gap(10)
            p300.dispense(etoh_volume+10, waste_reservoir.wells()[0].top())
            p300.blow_out(waste_reservoir.wells()[0].top())
            p300.drop_tip()

    # Dry at RT
    msg = "Drying the beads for " + str(drying_time) + " minutes. Protocol \
        will resume automatically."
    protocol.delay(minutes=drying_time, msg=msg)

    # Disengage MagDeck
    mag_deck.disengage()

    # Elute DNA
    p300.flow_rate.aspirate = 50
    p300.flow_rate.dispense = 50
    for index, column in enumerate(mag_plate.columns()[:num_cols]):
        p300.pick_up_tip()
        # add water/elution buffer to samples
        p300.transfer(
            elution_buffer_volume, water.bottom(1), column[0].bottom(3), new_tip='never'
        )
        # pipette up and down 5 times
        p300.mix(5, elution_buffer_volume, column[0].bottom(2))
        p300.move_to(column[0].top())
        p300.blow_out()
        # touch pipette tip to sides of well to knock off remaining liquid
        p300.touch_tip()
        p300.drop_tip()

    # Incubate at RT
    protocol.comment("Incubating the beads for "+str(settling_time)+" minutes. \
    Protocol will resume automatically.")
    protocol.delay(minutes=incubation_time)

    # engage magnet to clear beads after final elution
    if final_clear is True:
        mag_deck.engage()
        protocol.comment("Delaying for "+str(settling_time)+" minutes for \
            beads to settle.")
        protocol.delay(minutes=settling_time)

    # turn off lights
    protocol.set_rail_lights(False)

