import math

metadata = {
    'protocolName': 'Standard ampure/PEG clean ',
    'author': 'AMB, last updated 3/14/22',
    'description': 'Standard ampure/PEG clean up protocol',
    'apiLevel': '2.9'
}

def run(protocol):

########## EDIT THESE RUN OPTIONS AS NEEDED ##########

    # location of p300 multichannel ('left' or 'right', all lowercase and in single quotes)
    pipette_mount = 'left'

    # number of samples (note than the robot operates by columns, not rows)
    sample_count = 96

    # specify if adding beads or PEG ('beads' or 'peg', all lowercase and in single quotes)
    # if beads are used, they will be mixed before adding to samples to avoid beads settling
    # on the bottom of the reservoir
    beads_peg = 'beads'

    # volume of product that is being cleaned (ul)
    PCR_volume = 88

    # volume of ethanol to use for washes (ul) Max: 190
    # recommend 100 ul
    # if doing a full plate, can't go above 140 because the reservoir won't hold enough etoh
    # you can pause the protocol and refill reservoirs if necessary
    etoh_volume = 100

    # volume of ampure/PEG (ul)
    # Not recommended that PCR_volume + bead_volume >180 ul
    # well can hold total volume of 200 ul but when the pipette tip is inserted into the well it
    # can cause the volume to spill over the top of the well
    bead_volume = 62

    # volume of elution buffer (ul)
    elution_buffer_volume = 100

    # ampure/elution buffer incubation time (mins)
    incubation_time = 10

    # time for beads to settle on magnet (mins)
    # magnet is weaker than the usual one, beads will need longer to settle
    # time will depend on volume of beads
    # recommend 10-12 mins for 62 ul ampure
    settling_time = 12

    # time to let beads dry after ethanol washes (mins)
    # recommend 0 minute if doing whole plate
    # first columns will have been drying for awhile (~10 mins) by the time final column is done
    # and final column will be done drying by the time its eluted
    drying_time = 0

    # engage magnet at end of protocol to clear beads after elution (True or False, make sure first letter capitalized)
    final_clear = False


########## DO NOT EDIT BELOW THIS LINE ##########

    # turn on lights if not on already
    protocol.set_rail_lights(True)

    # checks
    if sample_count > 96 or sample_count < 1:
        raise Exception('Invalid number of samples.')
    total_vol = bead_volume + PCR_volume
    if total_vol > 200:
        raise Exception('Volume too high. Wells can hold maximum 200 uL. Reduce volume of DNA to be cleaned or volume of ampure/PEG')
    if elution_buffer_volume > 200:
        raise Exception('Elution buffer volume too high. Wells can hold maximum 200 uL. Reduce volume and try again.')
    if etoh_volume > 190:
        raise Exception('Volume of ethanol too high. Reduce volume and try again.')

    # Define hardware, pipettes/tips, plates
    # specify tips and slots
    tips300 = [
     protocol.load_labware(
      'opentrons_96_filtertiprack_200ul', str(slot)) for slot in [
      2, 3, 6]]
    # specify pipette, mount location, and tips
    p300m = protocol.load_instrument("p300_multi_gen2", mount = pipette_mount, tip_racks=tips300)
    # load magnetic module and specify slot
    mag_deck = protocol.load_module('magnetic module gen2', '1')
    # specify labware palced in magnetic module
    mag_plate = mag_deck.load_labware('biorad_96_wellplate_200ul_pcr')
    # specify waste labware and slot
    waste_reservoir = protocol.load_labware('liquid_waste_reservoir', '11')
    # specify reagent labware, reagents in each well, and slot on deck
    reagent_reservoir = protocol.load_labware(
        'nest_12_reservoir_15ml', '7')
    [beads, etoh_1, etoh_2, water] = [
        reagent_reservoir.wells_by_name()[well] for well in [
        'A1', 'A3', 'A4', 'A6']]

    # helper functions for tip parking
    named_tips = {}
    def name_the_tips(tip_box, name_list, well_list):
        for name in name_list:
            if name != 'current_tip':
                if name not in named_tips.keys():
                    named_tips[name] = []
        for name, well in zip(name_list, well_list):
            if name != 'current_tip':
                named_tips[name].append(tip_box[well])
            else:
                named_tips[name] = tip_box[well]
    def capture_current_starting_tip():
        for index, box in enumerate(tips300):
            if box.next_tip() is not None:
                current_starting_tip = box.next_tip()
                name_the_tips(tips300[index], ['current_tip'], [
                 current_starting_tip.well_name])
                return (tips300[index], current_starting_tip.well_name)


    # number of sample columns
    num_cols = math.ceil(sample_count / 8)
    # number of groups for ethanol washes
    num_groups = math.ceil(num_cols/3)
    if num_groups == 1:
        grps = [[0, num_cols]]
    elif num_groups == 2:
        grps = [[0, 3], [3, num_cols]]
    elif num_groups == 3:
        grps = [[0, 3], [3, 6], [6, num_cols]]
    elif num_groups == 4:
        grps = [[0, 3], [3, 6], [6, 9], [9, num_cols]]
    else:
        raise Exception("Invalid number of groups")

    # If doing half a plate just elute as normal but if doing a full plate
    # need to add water halfway through the 2nd ethanol wash so beads aren't overdried
    if num_groups == 1 or num_groups == 2:
        elute_groups = 1
        elute_cols = [[0, num_cols]]
    if num_groups == 3 or num_groups == 4:
        elute_groups = 2
        elute_cols = [[0, 6], [6, num_cols]]
    else:
        raise Exception("Invalid number of groups")

    # Add ampure/PEG
    for index, column in enumerate(mag_plate.columns()[:num_cols]):
        ccst = capture_current_starting_tip()
        name_the_tips(ccst[0], ['sup_tips'], [
            named_tips['current_tip'].well_name])
        p300m.pick_up_tip()
        # if adding beads, mix 2 times before pipetting
        p300m.flow_rate.aspirate = 100
        p300m.flow_rate.dispense = 100
        if beads_peg == 'beads':
            p300m.mix(2, 150, beads.bottom(1))
        p300m.flow_rate.aspirate = 50
        p300m.flow_rate.dispense = 50
        # add specified volume of beads/PEG to samples
        p300m.transfer(
         bead_volume, beads.bottom(1), column[0].bottom(3), new_tip='never')
        # pipette up and down 5 times
        p300m.mix(5, (bead_volume + PCR_volume), column[0].bottom(2))
        p300m.move_to(column[0].top())
        p300m.blow_out()
        # touch pipette tip to side of wells to knock off any remaining liquid
        p300m.touch_tip()
        p300m.return_tip()

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
        p300m.pick_up_tip(named_tips['sup_tips'][index])
        p300m.move_to(column[0].top())
        # aspirate really slowly to limit amount of beads
        p300m.flow_rate.aspirate = 5
        p300m.flow_rate.dispense = 100
        # limits up/down movement speed of pipette
        protocol.max_speeds['Z'] = 10
        p300m.aspirate(total_vol, column[0].bottom(1))
        p300m.move_to(column[0].top())
        protocol.max_speeds['Z'] = None
        protocol.delay(seconds=1)
        # dispense in waste reservoir
        p300m.dispense(total_vol, waste_reservoir.wells()[0].top())
        p300m.blow_out(waste_reservoir.wells()[0].top())
        p300m.return_tip()

    # EtOH wash 1
    # loop through groups
    for g in range(0, num_groups):
        p300m.flow_rate.aspirate = 100
        p300m.flow_rate.dispense = 150
        p300m.pick_up_tip()
        # add ethanol to each column in current group
        for index, column in enumerate(mag_plate.columns()[grps[g][0]:grps[g][1]], grps[g][0]):
            p300m.transfer(
                etoh_volume, etoh_1.bottom(1), column[0].top(-1), new_tip='never')
            p300m.move_to(column[0].top())
            p300m.blow_out()
            protocol.delay(seconds=1)
        p300m.drop_tip()

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
            p300m.flow_rate.aspirate = 40
            p300m.flow_rate.dispense = 150
            p300m.pick_up_tip(named_tips['sup_tips'][index])
            p300m.move_to(column[0].top())
            protocol.max_speeds['Z'] = 10
            p300m.aspirate(etoh_volume, column[0].bottom(1))
            p300m.move_to(column[0].top())
            protocol.max_speeds['Z'] = None
            protocol.delay(seconds=1)
            p300m.air_gap(10)
            p300m.dispense(etoh_volume + 10, waste_reservoir.wells()[0].top())
            p300m.blow_out(waste_reservoir.wells()[0].top())
            p300m.return_tip()

    # EtOH wash 2
    for g in range(0, num_groups):
        p300m.flow_rate.aspirate = 100
        p300m.flow_rate.dispense = 150
        p300m.pick_up_tip()

        # Add etoh
        for index, column in enumerate(mag_plate.columns()[grps[g][0]:grps[g][1]], grps[g][0]):
            p300m.transfer(
                etoh_volume, etoh_2.bottom(1), column[0].top(-1), new_tip='never')
            p300m.move_to(column[0].top())
            p300m.blow_out()
            protocol.delay(seconds=1)
        p300m.drop_tip()

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
            p300m.flow_rate.aspirate = 40
            p300m.flow_rate.dispense = 150
            p300m.pick_up_tip(named_tips['sup_tips'][index])
            p300m.move_to(column[0].top())
            protocol.max_speeds['Z'] = 10
            p300m.aspirate(etoh_volume, column[0].bottom(1))
            p300m.move_to(column[0].top())
            protocol.max_speeds['Z'] = None
            protocol.delay(seconds=1)
            p300m.air_gap(10)
            p300m.dispense(etoh_volume+10, waste_reservoir.wells()[0].top())
            p300m.blow_out(waste_reservoir.wells()[0].top())
            p300m.drop_tip()

        # add water to the first 6 columns if doing a full plate so beads don't over dry
        # they will be mixed later
        if elute_groups == 2:
            # add water after doing 2nd set of columns
            if g == 2:
                for index, column in enumerate(mag_plate.columns()[elute_cols[0][0]:elute_cols[0][1]], elute_cols[0][0]):
                    p300m.pick_up_tip()
                    # add water/elution buffer to samples
                    p300m.transfer(
                        elution_buffer_volume, water.bottom(1), column[0].top(), new_tip='never')

    # Dry at RT
    # Only needed if doing an odd number of groups
    if num_groups == 1 or num_groups == 3:
        msg = "Drying the beads for 2 minutes. Protocol \
            will resume automatically."
        protocol.delay(minutes=2, msg=msg)

    # Disengage MagDeck
    mag_deck.disengage()

    # Elute DNA
    p300m.flow_rate.aspirate = 50
    p300m.flow_rate.dispense = 50
    # if one elution group just add water/mix as normal
    if elute_groups == 1:
        for index, column in enumerate(mag_plate.columns()[:num_cols]):
            p300m.pick_up_tip()
            # add water/elution buffer to samples
            p300m.transfer(
                elution_buffer_volume, water.bottom(1), column[0].bottom(3), new_tip='never')
            # pipette up and down 5 times
            p300m.mix(5, elution_buffer_volume, column[0].bottom(2))
            p300m.move_to(column[0].top())
            p300m.blow_out()
            p300m.touch_tip()
            p300m.drop_tip()
    # if 2 elution groups need to go back and mix water/beads from first group
    if elute_groups == 2:
        for index, column in enumerate(mag_plate.columns()[elute_cols[0][0]:elute_cols[0][1]], elute_cols[0][0]):
            p300m.pick_up_tip(named_tips['sup_tips'][index])
            p300m.mix(5, elution_buffer_volume, column[0].bottom(2))
            p300m.move_to(column[0].top())
            p300m.blow_out()
            p300m.touch_tip()
            p300m.drop_tip()
        # then add water/mix rest of samples
        for index, column in enumerate(mag_plate.columns()[elute_cols[1][0]:elute_cols[1][1]], elute_cols[1][0]):
            p300m.pick_up_tip()
            # add water/elution buffer to samples
            p300m.transfer(
                elution_buffer_volume, water.bottom(1), column[0].bottom(3), new_tip='never')
            # pipette up and down 5 times
            p300m.mix(5, elution_buffer_volume, column[0].bottom(2))
            p300m.move_to(column[0].top())
            p300m.blow_out()
            p300m.touch_tip()
            p300m.drop_tip()

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

