import requests
from random import randint
from pprint import pprint

api_url = 'https://swapi.co/api/'
api_paths = requests.get('https://swapi.co/api/').json()
hints = {}


def filter_list(values, key, val, debug):
    def cb(item):
        if debug:
            print(item[key])
        return item[key] == val

    return list(filter(lambda d: cb(d), values))


def get_api_data(data_type='planets', page_no=1):
    try:
        url = '{0}?page={1}'.format(api_paths[data_type], page_no)
        return requests.get(url).json()

    except:
        pprint('Wrong request type: {}'.format(data_type))
        # pprint(api_paths)
        return False


def find_item(data_type='planets', key='name', val='Tatooine', page_no=1, debug=False):
    page = get_api_data(data_type, page_no)
    results = []
    try:
        results = filter_list(values=page['results'], key=key, val=val, debug=debug)
        print('Found {} results for {}: {} on page {} of {}.'.format(len(results), key, val, page_no, type))

        if results:
            return results
        elif page['next']:
            page_no += 1
            return find_item(data_type, key, val, page_no)
        else:
            return results

    except:
        return results


def filter_keys(obj, keys):
    data = {}
    try:
        for key in keys:
            if key in obj:
                data[key] = obj[key]
    except:
        print('Something went wrong.')
    finally:
        return data


def save_results(sources, keys, file_name='_', append_bmi=False):
    file_name += '.txt'
    file = open(file_name, 'w')

    if len(sources):
        for i, source in enumerate(sources):
            data = requests.get(source).json()
            data_filtered = filter_keys(data, keys)
            print('Saving result {} of {}...'.format(i+1, len(sources)))
            if append_bmi:
                file.write('bmi: ' + str(get_bmi(data['mass'], data['height'])) + ', ')
            for j, item in enumerate(data_filtered):
                file.write('{}: {}'.format(item, data[item]))
                if j == len(data_filtered) - 1:
                    file.write('\n')
                else:
                    file.write(', ')
    else:
        file.write('Nothing to see here.')

    file.close()
    print('Saved {} results in {}.'.format(len(sources), file_name))


def get_residents(planet='Tatooin', debug=False):
    planet_data = find_item(data_type='planets', key='name', val=planet, debug=debug)
    residents = []
    keys = ['name', 'gender', 'birth_year', 'height', 'mass']

    try:
        residents = planet_data[0]['residents']
    finally:
        print('Found {0} residents of {1}.'.format(len(residents), planet))
        save_results(residents, keys, 'residents-' + planet.lower().replace(' ', '-'))
        return residents


def get_episode_species(episode_id='1', debug=False):
    film_data = find_item(data_type='films', key='episode_id', val=episode_id, debug=debug)
    species = []
    keys = ['name']

    try:
        species = film_data[0]['species']
    finally:
        print('Found {0} species in episode {1}.'.format(len(species), episode_id))
        save_results(species, keys, 'species-episode-' + str(episode_id))

    return species


def get_species_people(species='Gungan', debug=False):
    specie_data = find_item(data_type='species', key='name', val=species, debug=debug)
    people = []
    keys = ['name', 'gender']

    try:
        people = specie_data[0]['people']
    finally:
        print('Found {0} people of {1}.'.format(len(people), species))
        save_results(people, keys, 'people-' + species.lower().replace(' ', '-'))

    return people


def get_bmi(weight=0, height=0):
    try:
        return round((int(weight) / int(height) ** 2) * 100, 2) * 100
    except:
        return 0


def get_pilots_bmi(starship='Millennium Falcon', debug=False):
    ships = find_item(data_type='starships', key='name', val=starship, debug=debug)
    pilots = []
    keys = ['name', 'gender', 'height', 'mass']

    try:
        pilots = ships[0]['pilots']
    finally:
        print('Found {0} pilots of {1}.'.format(len(pilots), starship))
        save_results(pilots, keys, starship.lower().replace(' ', '-') + '-pilots', append_bmi=True)

    return pilots


def select_value(values, intro=''):
    message = intro + '\n'

    for i, value in enumerate(values):
        message += '{}: {}'.format(i+1, value)
        if i < len(values)-1:
            message += ', '
        else:
            message += '\n'

    try:
        selected = int(input(message))
        if selected not in range(1, len(values) + 1):
            raise ValueError('Bad input!')
        option = values[selected-1]
        print('Selected {}: {}'.format(values.index(option)+1, option))
    except:
        selected = randint(0, len(values) - 1)
        option = values[selected]
        print('Invalid input. Selected {}: {}'.format(selected + 1, option))

    return option


def get_keys(data_type='planets', key='name', page_no=1):
    page = get_api_data(data_type, page_no)
    items = []

    while page_no:
        try:
            results = page['results']
            print('Collecting {} {} hints from page {}...'.format(type, key, page_no))
            for result in results:
                if result[key] not in items:
                    items.append(result[key])

            page_no += 1
            page = get_api_data(data_type, page_no)

        except:
            page_no = 0

    return items


def start():
    types = ['get_species_people', 'get_episode_species', 'get_residents', 'get_pilots_bmi']
    selected = types.index(select_value(types, 'Start search: '))

    if selected == 0:
        if 'species' not in hints:
            hints['species'] = get_keys('species', 'name') or []

        species = select_value(hints['species'], 'Species: ')
        # debug = input('Debug? y/n: ') == 'y'
        get_species_people(species)

    elif selected == 1:
        if 'films' not in hints:
            hints['films'] = get_keys('films', 'episode_id') or []
            hints['films'].sort()

        episode_id = select_value(hints['films'], 'Episode: ')
        # debug = input('Debug? [y/any key]: ') == 'y'
        get_episode_species(episode_id)

    elif selected == 2:
        if 'planets' not in hints:
            hints['planets'] = get_keys('planets', 'name') or []

        planet = select_value(hints['planets'], 'Planet: ')
        # debug = input('Debug? [y/any key]: ') == 'y'
        get_residents(planet)

    elif selected == 3:
        if 'starships' not in hints:
            hints['starships'] = get_keys('starships', 'name') or []

        starship = select_value(hints['starships'], 'Starship: ')
        # debug = input('Debug? [y/any key]: ') == 'y'
        get_pilots_bmi(starship)

    again = input('Try again? [y/any key]: ') == 'y'
    if again:
        start()


start()
