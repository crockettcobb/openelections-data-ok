from __future__ import print_function, division

import pandas as pd

positions = ['President', 'U.S. Senate', 'U.S. House',
            'State Senate','State House', 'Governor']

def parse_2016():
    '''Reads in CSV from Oklahoma Elections and parses into OpenElections
    format.
    '''
    df = pd.read_csv(
        'http://www.ok.gov/elections/support/20161108_prec_csv.zip')

    df = df.rename(columns={'county_name': 'county',
                            'race_description': 'office',
                            'cand_absmail_votes': 'mail_votes',
                            'cand_early_votes': 'early_votes',
                            'cand_elecday_votes': 'elec_day_votes',
                            'cand_tot_votes': 'total_votes',
                            'cand_name': 'candidate',
                            'cand_party': 'party',
                            'precinct_code': 'precinct'})

    df = df.drop(['elec_date', 'race_number', 'race_party', 'cand_number',
                  'entity_description', 'tot_race_prec',
                  'race_prec_reporting'], axis=1)

    # extract district information
    df['district'] = df['office'].str.extract('(\d{1,2})', expand=True)

    # clean up office descriptions
    df.loc[df['office'].str.contains(
        'PRESIDENT'), 'office'] = 'President'
    df.loc[df['office'].str.contains(
        'UNITED STATES SENATOR'), 'office'] = 'U.S. Senate'
    df.loc[df['office'].str.contains(
        'UNITED STATES REPRESENTATIVE'), 'office'] = 'U.S. House'
    df.loc[df['office'].str.contains(
        'STATE REPRESENTATIVE'), 'office'] = 'State House'
    df.loc[df['office'].str.contains(
        'STATE SENATOR'), 'office'] = 'State Senate'

    # select only the positions of interest
    df = df[df['office'].isin(positions)].copy()

    # clean up candidate names
    df.loc[df['candidate'].str.contains(
        'CLINTON'), 'candidate'] = 'Hillary Clinton'
    df.loc[df['candidate'].str.contains(
        'JOHNSON'), 'candidate'] = 'Gary Johnson'
    df.loc[df['candidate'].str.contains(
        'TRUMP'), 'candidate'] = 'Donald Trump'
    df.loc[df['candidate'].str.contains(
        'JUSTIN JJ HUMPHREY', case=False), 'candidate'] = 'Justin Humphrey'
    df.candidate = df.candidate.str.title()
    df.candidate = df.candidate.str.replace(r'^(\S+)\s+(.*\b).\s+(\S+)$',
                                            "\\1 \\3").astype('str')
    # melt the votes together
    # dfm = pd.melt(df, id_vars=['county', 'precinct_code', 'office',
    #                         'cand_name', 'cand_party', 'district'],
    #                 value_vars=['Early', 'In-Person', 'Absentee', 'Total'],
    #                 value_name='votes')

    df.county = df.county.str.title()

    # https://www.ok.gov/elections/support/20161108_seb.html
    dft = df.groupby(['office', 'candidate']).agg({'total_votes': 'sum'})
    assert dft.loc['President'].total_votes.sum() == 1452992
    assert dft.loc['U.S. Senate'].total_votes.sum() == 1448047
    assert dft.loc['U.S. House'].total_votes.sum() == 1133244

    df.to_csv('2016/20161108__ok__general__precinct.csv', index=False)

if __name__ == '__main__':
    parse_2016()
