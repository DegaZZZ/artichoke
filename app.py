from flask import Flask, render_template, send_file
from DeckDecoder import DeckDecoder, DeckDecodingException
from opengraph_gen import create_open_graph_image
import json
import io
import binascii

app = Flask(__name__)

# Dummy data - replace with your database logic
decks = [
    {"id": 1, "author": "Valve", "code": "ADCJQUQI30zuwEYg2ABeF1Bu94BmWIBTEkLtAKlAZakAYmHh0JsdWUvUmVkIEV4YW1wbGU_"},
    {"id": 2, "author": "degaz", "code": "ADCJUoIPrgCScMEldUFq7sCWaEBkEOBjIRVgQOMpANSaXggUm9sbA__"},
    {"id": 30, "author": "kompot", "code": "ADCJcwEJLkCCg5Mjbi7AoSpAZNiAUGDcgFyAQoKiCQBbwGI0YDQtA__"},
    {"id": 3, "code": "ADCJcUiL7kCQYsNCbhdgXfdAUqrAZqfpQNIhI9oAXIBWyBCbHVlIC8gR3JlZW4gXSBIWVBFRCBXaW5uZXIgRGVjaw__"},
    {"id": 4, "code": "ADCJcYbKrkCBYwNSbC7AkqCaQFaXENBTyIBswGIk2gBcgFbRHVhbC1VR10gVGh1bmRlcmNoYWQgQ29tYm8_"},
    {"id": 5, "author": "Slacks", "code": "ADCJdYSLrkCjUMTBKq7AhCZRg6XAZ6LrAF3AaMBA42IQVJDQU5FICBBU1MtU0FMVCAy"},
    {"id": 6, "author": "Slacks", "code": "ADCJQATcbgCnAMMDnq7ApqCiEevARSIQUccuQG4AZdIb3N0YWdlIFNpdHVhdGlvbiEh"},
    {"id": 7, "author": "Slacks", "code": "ADCJWsPJX2xvAEFQQmjuwKYrQKBVIEZRBW-AaQBF02TQWkgUElULXkgdGhlIEZPTw__"},
    {"id": 8, "author": "Slacks", "code": "ADCJZgbabkCCweKBWS9AkFIRUMDQYZFggJBAhCCAQEfAxNJbnRlcmVzdGluZyBJbXByb3ZlbWVudHMgdjI_"},
    {"id": 9, "author": "Slacks", "code": "ADCJU8OtLgCGgJEBzq7AmsBVEaGSwSUlJiCbQF1AYZ0AYdLRUVQTyBEQSBNRUVQTw__"},
    {"id": 10, "author": "Slacks", "code": "ADCJS8bJLkChEUBJwGnuwJHAYKHCo2EgWcCQoFyASEFSE1vbm8gUmVkIE9vcHMhIEFsbCBDcmVlcHMgMg__"},
    {"id": 11, "author": "Slacks", "code": "ADCJckMMbgCHYFWELe7AoEnAhWJixOZNQFChJ+FC7oBAU1SIFRPU1NFUiEhIQ__"},
    {"id": 12, "author": "Slacks", "code": "ADCJeMWL7kCBYJFAaO7Api+AYxYgRlEFb8BpAFkAZNBUGl0IEZpZ2h0ZXIgZm9yIFNsYWNrcw__"},
    {"id": 13, "author": "Slacks", "code": "ADCJdgLYbkCBoITA766Ao2LjbIBg4FlAUdLQSUBvAGGpAJSQVZFTiBTSE9PSw__"},
    {"id": 14, "author": "Slacks", "code": "ADCJfYOPrgCTAQRgye7AlWIj6UBjYSUgolGngi3Ah+vAVJJWC1ZIEJVSVNORVNT"},
    {"id": 15, "author": "Slacks", "code": "ADCJaIUIbkCSBeCD629AoSHR4GGgoGCE1OjAYJST09NIEZPUiBJTVBST1ZFTUVOVA__"},
    {"id": 16, "author": "Slacks", "code": "ADCJbsPIH2qvAESBkN6uwKckoRTikeNEUEBAQevApeVilRIRSBMT05HIEhBVUwgMg__"},
    {"id": 17, "code": "ADCJcURIH0De7sBKAGQeF1BQWbdAVhHRwFIMQIECG0CTgIfRlBCdQFSZWQtR3JlZW4gQnJhd2xlcg__"},
    {"id": 18, "code": "ADCJSY6NrgCWQyTAy29ApKeQUFDoQOIRCIBgpORlI1Td2ltJmFwb3M7cyA0My1jYXJkIG1vbm9ibHVlICsgR1VJREUgKFdpbm5pbmcgRGVjayBvZiBNV0Mp"},
    {"id": 19, "code": "ADCJcsMNrgCWRCMPQ6muwKrAoGUl4FSQXoCkaMCBYaOUk9MTElOIFNUT1JN"},
    {"id": 20, "code": "ADCJckgrbkCARFLC6a7AoGFjJuoArEBgVQhAYcNglJlZC9CbGFjayAtIHBlcmZlY3Qgc3RhcnRlciBkZWNr"},
    {"id": 21, "code": "ADCJZwPNrgCF06WBLhdoN4Bm0FGZQGfElGhAkF1AUakAUpSZWQgQmx1ZSBCdWRnZXQ_"},
    {"id": 22, "code": "ADCJekMNrgCGI1WBHi7AlsaUlCOgUExAXIBgYi7AXIBgVJlZCBCbHVlIDMuMA__"},
    {"id": 23, "code": "ADCJYEQPrgCAhBElDhdAUEl3QEBUEYFAQsPCAoDTUEBC0sKAwNCAQEBAgEBAQICQQEBAQQLAQEFRAECBAECJQEEFQoNCwcDBYUBAw4HR3JlZW4gUmFtcCBjaGVhcA__"},
    {"id": 24, "code": "ADCJQoZJrkCCI1WBHi7AltBBpNSXEKBMgEErgEBSAsiAQ5yAYFHTklLIC0gIENvbnRyb2wvQWdncm8gNS0w"},
    {"id": 25, "code": "ADCJfcSNrgCWQyVAThdQrDdARBlAiABUpATJgGJSKYBgoQBX5SBQnVkZ2V0IE1vbm9ibHVlIHYy"},
    {"id": 26, "code": "ADCJbgPMbgCBWUBlQE4XUKw3QEQZQIgAVKQEyYBia4BgoQBX5SBQnVkZ2V0IE1vbm9ibHVl"},
    {"id": 27, "code": "ADCJSwUfrgCCQ2LDGC7AoaGSoVVQaABOAFBAgNMR1+mAUJvQkQgQmVubnkgQnVmZm5hc3Np"},
    {"id": 28, "code": "ADCJcQQL7kCQQsNibhduN0BSqsBml6BMgGzAUiEj2gBMgFCbHVlL0dyZWVuIEJydW1h"},
    {"id": 29, "code": "ADCJRwSJX2Dc7wBEAN4XUFBcN0BQmQBQWABRCgBCgN0AWUBbQFDbwEISEJsdWUtQmxhY2sgQ29udHJvbA__"},
]

deck_codes = [
    "ADCJQUQI30zuwEYg2ABeF1Bu94BmWIBTEkLtAKlAZakAYmHh0JsdWUvUmVkIEV4YW1wbGU_", "ADCJbYiZLkCwQTBBQinAWe7ApGbqAICQXIBuQGNl2QBIAFIVmluS2Vsc2llcidzIFJpc2luZyBBbmdlciBtb25vIHJlZA__"
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

    parsed_decks = []

    for deck_temp in decks:
        try :
            deck = DeckDecoder.decode(deck_temp.get('code'))
        except DeckDecodingException as e:
            return "Something wrong just happened"
        except binascii.Error as b:
            return "Something wrong just happened" 
        
        heroes_deck = deck['heroes']
        cards_deck = deck['cards']

        item_cards_data = []
        for card in cards_deck:
            for item in item_cards:
                if card['card_id'] == item['card_id']:
                    item_cards_data.append({'card_id': item['card_id'], 'card_name': item['card_name']['english'], 'count': card['count'], 'gold_cost': item['gold_cost'], 'mini_image': item['mini_image']['default']})

        #Total amount of item_cards (sum of counts)
        total_item_cards = 0
        for item in item_cards_data:
            total_item_cards += item['count']

        #Get all heroes in a deck
        heroes = []
        for hero in heroes_deck:
            for card in hero_cards:
                if hero['card_id'] == card['card_id']:
                    heroes.append(card)

        heroes_images = []
        for hero in heroes:
            heroes_images.append(hero['mini_image']['default'])

        # Get deck name
        deck_name = deck['name']

        # Get deck author
        deck_author = deck_temp.get('author')

        # Get unique colours in deck
        colours = []
        for hero in heroes:
            if 'is_blue' in hero:
                colours.append('#3474c3')
            elif 'is_red' in hero:
                colours.append('#d3443c')
            elif 'is_black' in hero:
                colours.append('#332c47')
            elif 'is_green' in hero:
                colours.append('#479036')
        colours = list(set(colours))



        parsed_decks.append({'deck_code': deck_temp.get('code'), 'author': deck_author, 'colours': colours, 'deck_name': deck_name, 'heroes': heroes_images, 'item_count': total_item_cards})

    return render_template('index.html', decks=parsed_decks)

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
