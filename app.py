from flask import Flask, render_template, send_file
from DeckDecoder import DeckDecoder, DeckDecodingException
from opengraph_gen import create_open_graph_image
import json
import binascii
import io

app = Flask(__name__)

# Dummy data - replace with your database logic
decks = [
    {"id": 1, "name": "Deck One", "code": "ADCJQUQI30zuwEYg2ABeF1Bu94BmWIBTEkLtAKlAZakAYmHh0JsdWUvUmVkIEV4YW1wbGU_", "colors": "Blue, Red", "avg_mana": "2.5", "type": "Aggro"},
    {"id": 2, "name": "Deck One", "cost": "Low", "colors": "Blue, Red", "avg_mana": "2.5", "type": "Aggro"},
    {"id": 3, "name": "Deck One", "cost": "Low", "colors": "Blue, Red", "avg_mana": "2.5", "type": "Aggro"},
    {"id": 4, "name": "Deck One", "cost": "Low", "colors": "Blue, Red", "avg_mana": "2.5", "type": "Aggro"},
    {"id": 5, "name": "Deck One", "cost": "Low", "colors": "Blue, Red", "avg_mana": "2.5", "type": "Aggro"},
]

with open('card_set_1.json', encoding='utf-8') as json_file:
    data1 = json.load(json_file)

with open('card_set_0.json', encoding='utf-8') as json_file:
    data0 = json.load(json_file)

card_list_1 = data1['card_set']['card_list']
card_list_0 = data0['card_set']['card_list']



#Get all item cards in a card sets
item_cards = []
for card in card_list_1:
    if card['card_type'] == 'Item':
        item_cards.append(card)

for card in card_list_0:
    if card['card_type'] == 'Item':
        item_cards.append(card)

#Get all hero cards in a card list
hero_cards = []
for card in card_list_1:
    if card['card_type'] == 'Hero':
        hero_cards.append(card)

for card in card_list_0:
    if card['card_type'] == 'Hero':
        hero_cards.append(card)

#Get all spell cards in a card list
spell_cards = []
for card in card_list_1:
    if card['card_type'] == 'Spell':
        spell_cards.append(card)

for card in card_list_0:
    if card['card_type'] == 'Spell':
        spell_cards.append(card)

#Get all creep cards in a card list
creep_cards = []
for card in card_list_1:
    if card['card_type'] == 'Creep':
        creep_cards.append(card)

for card in card_list_0:
    if card['card_type'] == 'Creep':
        creep_cards.append(card)
    
#Get all improvement cards in a card list
improvement_cards = []
for card in card_list_1:
    if card['card_type'] == 'Improvement':
        improvement_cards.append(card)

for card in card_list_0:
    if card['card_type'] == 'Improvement':
        improvement_cards.append(card)


@app.route('/')
def index():
    return render_template('index.html', decks=decks)

@app.route('/deck-preview/<deck_code>')
def deck_preview(deck_code):

    try :
        deck = DeckDecoder.decode(deck_code)
    except DeckDecodingException as e:
        return "What the actual fuck is this deck?"
    except binascii.Error as b:
        return "What the actual fuck is this deck?"    
    
    heroes_deck = deck['heroes']

    #Get all heroes in a deck
    heroes = []
    for hero in heroes_deck:
        for card in hero_cards:
            if hero['card_id'] == card['card_id']:
                heroes.append(card)

    heroes_images = []
    for hero in heroes:
        heroes_images.append(hero['large_image']['default'])
    
    img = create_open_graph_image(heroes_images)

    # Save the image to a BytesIO object in memory
    img_io = io.BytesIO()
    img_format = 'PNG'  # or 'JPEG', depending on your needs
    img.save(img_io, img_format)
    img_io.seek(0)

    return send_file(img_io, mimetype=f'image/{img_format.lower()}')

@app.route('/deck/<deck_code>')
def deck_detail(deck_code):

    try :
        deck = DeckDecoder.decode(deck_code)
    except DeckDecodingException as e:
        return "What the actual fuck is this deck?"
    except binascii.Error as b:
        return "What the actual fuck is this deck?"
    
    
    heroes_deck = deck['heroes']
    cards_deck = deck['cards']
    deck_name = deck['name']

    #Get all heroes in a deck
    heroes = []
    for hero in heroes_deck:
        for card in hero_cards:
            if hero['card_id'] == card['card_id']:
                heroes.append(card)

    heroes_images = []
    for hero in heroes:
        heroes_images.append(hero['large_image']['default'])

    #create_open_graph_image(heroes_images, f'open_graphs/{deck_code}.jpg')

    item_cards_data = []
    for card in cards_deck:
        for item in item_cards:
            if card['card_id'] == item['card_id']:
                item_cards_data.append({'card_id': item['card_id'], 'card_name': item['card_name']['english'], 'count': card['count'], 'gold_cost': item['gold_cost'], 'mini_image': item['mini_image']['default']})

    #Sort item cards by gold cost
    item_cards_data.sort(key=lambda x: x['gold_cost'])

    main_deck = []
    for card in cards_deck:
        for ability in spell_cards:
            if card['card_id'] == ability['card_id']:
                main_deck.append(ability)

    for card in cards_deck:
        for creep in creep_cards:
            if card['card_id'] == creep['card_id']:
                main_deck.append(creep)

    for card in cards_deck:
        for improvement in improvement_cards:
            if card['card_id'] == improvement['card_id']:
                main_deck.append(improvement)

    references = []
    for hero in heroes:
        references.append(hero['references'])

    #Get card by card id from each reference
    card_references = []
    for reference in references:
        for card in card_list_1:
            if reference[0]['card_id'] == card['card_id']:
                card_references.append(card)

    #Data structure for card_references
    card_references_data = []
    #add count to card references
    for card in card_references:
        for hero in references:
            for reference in hero:
                if card['card_id'] == reference['card_id']:
                    card['count'] = reference['count']

        card_references_data.append({'card_id': card['card_id'], 'card_name': card['card_name']['english'], 'count': card['count'], 'mana_cost': card['mana_cost'], 'mini_image': card['mini_image']['default']})

    main_deck_data = []
    for card in cards_deck:
        for spell_creeps in main_deck:
            if card['card_id'] == spell_creeps['card_id']:
                main_deck_data.append({'card_id': spell_creeps['card_id'], 'card_name': spell_creeps['card_name']['english'], 'count': card['count'], 'mana_cost': spell_creeps['mana_cost'], 'mini_image': spell_creeps['mini_image']['default']})

    final_list = card_references_data + main_deck_data

    for card in final_list:
        #find card in card_list with same card_id and place in temp_card
        for temp_card in card_list_1:
            if card['card_id'] == temp_card['card_id']:
                break
        #check if card has a key is_blue, is_red, is_black or is_green in the temp_card
        if 'is_blue' in temp_card:
            card['colour'] = 'blue'
            card['CSSValue'] = 'DeckViewer_CardList_CardContainerU'
        elif 'is_red' in temp_card:
            card['colour'] = 'red'
            card['CSSValue'] = 'DeckViewer_CardList_CardContainerR'
        elif 'is_black' in temp_card:
            card['colour'] = 'black'
            card['CSSValue'] = 'DeckViewer_CardList_CardContainerB'
        elif 'is_green' in temp_card:
            card['colour'] = 'green'
            card['CSSValue'] = 'DeckViewer_CardList_CardContainerG'

    
    #Sort final list by mana cost
    final_list.sort(key=lambda x: x['mana_cost'])

    if deck:
        # Make sure to include main_deck_cards and item_deck_cards in your deck data
        return render_template('deck_details.html', deck_name=deck_name, deck_code=deck_code, item_cards=item_cards_data, cards=final_list, heroes=heroes)
    else:
        # Handle the case where the deck doesn't exist
        return "Deck not found", 404



if __name__ == '__main__':
    app.run(debug=True)
