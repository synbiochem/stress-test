'''
synbiochem (c) University of Manchester 2018

synbiochem is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import sys

from Bio.Alphabet import IUPAC
from Bio.Seq import Seq
from synbiochem.utils import ice_utils, seq_utils
from enzyme import cluster


class Mutater(object):
    '''Class to represent a mutater.'''

    def __init__(self, url, username, password):
        self.__ice_client = ice_utils.ICEClient(url, username, password)

    def mutate(self, ice_id, mutations):
        '''mutate.'''

        # Get ICE entry:
        ice_entry = self.__ice_client.get_ice_entry(ice_id).copy()
        dna = ice_entry.get_dna()
        cds = [feat for feat in dna['features']
               if feat['typ'] == 'http://purl.obolibrary.org/obo/SO_0000316']

        print translate(dna['seq'][cds[0]['start'] - 1:cds[0]['end']])

        # Mutate:
        for aa_pos, mutation in mutations.iteritems():
            dna_pos = cds[0]['start'] - 1 + (aa_pos * 3)
            dna['seq'] = dna['seq'][:dna_pos] + \
                mutation + dna['seq'][dna_pos + 3:]

        # Update names:
        _update_names(mutations, ice_entry, dna)

        print translate(dna['seq'][cds[0]['start'] - 1:cds[0]['end']])

        return ice_entry

    def save(self, ice_entry):
        '''save.'''
        self.__ice_client.set_ice_entry(ice_entry)


def translate(dna_seq):
    '''Translate DNA seq.'''
    return Seq(dna_seq, IUPAC.ambiguous_dna).translate()


def _update_names(mutations, ice_entry, dna):
    '''Update names.'''
    mut_seq = ' (' + \
        ', '.join([':'.join([str(pos + 1), mut])
                   for pos, mut in mutations.iteritems()]) + \
        ')'

    metadata = ice_entry.get_metadata()
    metadata['name'] += mut_seq
    metadata['shortDescription'] += mut_seq
    dna['name'] += mut_seq
    dna['desc'] += mut_seq


def main(args):
    '''main.'''
    id_seqs = seq_utils.read_fasta(args[0])

    updated_pos = cluster.get_positions(id_seqs, args[1], args[2],
                                        [int(pos) for pos in args[8:]])

    mutater = Mutater(args[3], args[4], args[5])
    ice_entry = mutater.mutate(args[6],
                               {int(pos[2]): args[7] for pos in updated_pos})
    mutater.save(ice_entry)


if __name__ == '__main__':
    main(sys.argv[1:])
