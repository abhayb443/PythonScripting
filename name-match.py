import Levenshtein as lev
import indian_namematch
from indian_namematch import fuzzymatch
import fuzzywuzzy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re


a = [
'ANKUR SINGH',
'AMIT KUMAR',
'PRASANT KUMAR MEHER',
'Vijaya Kumar Sethupathi',
'Dinesh B Singh',
'SONALIBEN HIRALBHAI RATHOD',
'RAJVEER KAUR',
'DILIPBHAI SHEKH',
'RASHID ALI',
'LAKHAN SINH CHUNDAWAT',
'ANUJ SRIVASTAV',
]

b = [
'SAMEER SINGH',
'GYANENDRA KUMAR SING',
'SRIKANTA KUMAR SETHY',
'Vinitha Vijay Sethupathi',
'Rekha D Singh',
'NISHABENPRIYANKKUMAR',
'Mr BHUPINDER SINGH S',
'Mrs VARUNABEN DILIP',
'RASID S/O SHAMSHULHA',
'LAKHANSINGHBHAGWANSI',
'Mr ANUJ PREMNARAYAN',
]

c = [
'KARAN MUKESH MEHTA',
'MOHAMED MUSTUFA EBRAHIM DADA',
'NIMESH HARESHBHAI JANI',
'TANISH DHAWAN',
'RAJENDRASINH PRAVINSINH BIHOLA',
'HIRENKUMAR NAGINBHAI PRAJAPATI',
'AJESH A N KUMAR',
'MANISH MADHUKAR KHARATE',
'SONALIBEN HIRALBHAI RATHOD',
'AMARPREET SINGH',
'SANKETKUMAR KUBERBHAI PANDYA',
'BALKRUSHNKUMAR ARVINDBHAI NIMAVAT',
'SATISH DAS MAHANT',
'GAGANDEEP SINGH',
'MANISH KUMAR DEWANGAN',
'KIRANBHAI PRAVINBHAI PATEL',
'NARENDRA NANAKRAM AAHUJA',
'ANIL BHUMESHWAR CHATLA',
'SUDHEER KUMAR SOMARA',
'SHAILESHKUMAR BUDHABHAI BARIA',
'BARAD YOGENDRAKUMAR KHUMANSANG',
'MANISH CHOUHAN',
'JAVED AHMAD',
'NOMAN AHMED MOHAMMED YUSUF MUNSHI',
'NIKUNJ ASHOKBHAI PATEL',
'ATITKUMAR MAHENDRABHAI PRAJAPATI',
'PRANAY RAJENDRAKUMAR PATEL',
'POTULA SUBRAHMANYA MARKANDESWARARAO',
'DURGESH KUMAR MEHTA',
'NIRAJ',
'SOHEL SHABBIR ATTAR',
'JIAUL RAHMAN',
]

d = [
'KARANMMEHTA',
'MOHAMEDMUSTUFAEBRAHI',
'JANI NIMESH HARESHBH',
'TANISH DHAWAN S O MA',
'BIHOLA RAJENDRASINH',
'HIREN N PRAJAPATI',
'AJESH',
'Mr kharate Manish',
'RATHODSONALIBENHIRAL',
'AMARPREET SINGH',
'Mr SANKETKUMAR KUBE',
'Mr BALKRUSHNA ARVIN',
'Mr SATISH DAS MAHAN',
'GAGAN DEEP SINGH S',
'Mr. MANISH KUMAR D',
'Mr KIRANBHAI PRAVIN',
'Mr. NARENDRABHAI NAN',
'MRANILBHUMESHWARCHAT',
'SOMARA SUDHEER KUMAR',
'BARIA SHAILESHKUMAR',
'YOGENDRASINHKHUMANSU',
'Mr MANISH SO SHYAM',
'ZAWEDAHAMADSOSHAKILA',
'NOMAAN AHMED MOHAMME',
'Mr NIKUNJBHAI ASHOK',
'Atit Mahendrakumar P',
'Master PRANAY RAJESH',
'Mr P S MARKANDESWA',
'DURGESH S O ASHOK ME',
'NEERAJ KUMAR MISHRA',
'SOHAIL',
'Mr PARIMAL BARMAN',
]

e = [
'ANKUR SINGH',
'AMIT KUMAR',
'PRASANT KUMAR MEHER',
'Vijaya Kumar Sethupathi',
'Dinesh B Singh',
'SONALIBEN HIRALBHAI RATHOD',
'RAJVEER KAUR',
'DILIPBHAI SHEKH',
'RASHID ALI',
'LAKHAN SINH CHUNDAWAT',
'ANUJ SRIVASTAV',
'KARAN MUKESH MEHTA',
'MOHAMED MUSTUFA EBRAHIM DADA',
'NIMESH HARESHBHAI JANI',
'TANISH DHAWAN',
'RAJENDRASINH PRAVINSINH BIHOLA',
'HIRENKUMAR NAGINBHAI PRAJAPATI',
'AJESH A N KUMAR',
'MANISH MADHUKAR KHARATE',
'SONALIBEN HIRALBHAI RATHOD',
'AMARPREET SINGH',
'SANKETKUMAR KUBERBHAI PANDYA',
'BALKRUSHNKUMAR ARVINDBHAI NIMAVAT',
'SATISH DAS MAHANT',
'GAGANDEEP SINGH',
'MANISH KUMAR DEWANGAN',
'KIRANBHAI PRAVINBHAI PATEL',
'NARENDRA NANAKRAM AAHUJA',
'ANIL BHUMESHWAR CHATLA',
'SUDHEER KUMAR SOMARA',
'SHAILESHKUMAR BUDHABHAI BARIA',
'BARAD YOGENDRAKUMAR KHUMANSANG',
'MANISH CHOUHAN',
'JAVED AHMAD',
'NOMAN AHMED MOHAMMED YUSUF MUNSHI',
'NIKUNJ ASHOKBHAI PATEL',
'ATITKUMAR MAHENDRABHAI PRAJAPATI',
'PRANAY RAJENDRAKUMAR PATEL',
'POTULA SUBRAHMANYA MARKANDESWARARAO',
'DURGESH KUMAR MEHTA',
'NIRAJ',
'SOHEL SHABBIR ATTAR',
'JIAUL RAHMAN',
]

f = [
'SAMEER SINGH',
'GYANENDRA KUMAR SING',
'SRIKANTA KUMAR SETHY',
'Vinitha Vijay Sethupathi',
'Rekha D Singh',
'NISHABENPRIYANKKUMAR',
'Mr BHUPINDER SINGH S',
'Mrs VARUNABEN DILIP',
'RASID S/O SHAMSHULHA',
'LAKHANSINGHBHAGWANSI',
'Mr ANUJ PREMNARAYAN',
'KARANMMEHTA',
'MOHAMEDMUSTUFAEBRAHI',
'JANI NIMESH HARESHBH',
'TANISH DHAWAN S O MA',
'BIHOLA RAJENDRASINH',
'HIREN N PRAJAPATI',
'AJESH',
'Mr kharate Manish',
'RATHODSONALIBENHIRAL',
'AMARPREET SINGH',
'Mr SANKETKUMAR KUBE',
'Mr BALKRUSHNA ARVIN',
'Mr SATISH DAS MAHAN',
'GAGAN DEEP SINGH S',
'Mr. MANISH KUMAR D',
'Mr KIRANBHAI PRAVIN',
'Mr. NARENDRABHAI NAN',
'MRANILBHUMESHWARCHAT',
'SOMARA SUDHEER KUMAR',
'BARIA SHAILESHKUMAR',
'YOGENDRASINHKHUMANSU',
'Mr MANISH SO SHYAM',
'ZAWEDAHAMADSOSHAKILA',
'NOMAAN AHMED MOHAMME',
'Mr NIKUNJBHAI ASHOK',
'Atit Mahendrakumar P',
'Master PRANAY RAJESH',
'Mr P S MARKANDESWA',
'DURGESH S O ASHOK ME',
'NEERAJ KUMAR MISHRA',
'SOHAIL',
'Mr PARIMAL BARMAN',
]

New_list = zip(c, d)

results = {'True': 0, 'False':0}
for i in New_list:
    print(i)
    primary, secondary = i[0].lower().strip(), i[1].lower().strip()
    primary = re.sub("mrs|md|sepoy|mohmad|mohmed|mohmd|mohd|mohammad|mohammed|mhd|moh|mahammad|bhai|bai|rao|lal|ben|miss|mr.|mr|sri|dost|kumar", "", primary).strip()
    secondary = re.sub("mrs|md|sepoy|mohmad|mohmed|mohmd|mohd|mohammad|mohammed|mhd|moh|mahammad|bhai|bai|rao|lal|ben|miss|mr.|mr|sri|dost|kumar", "", secondary).strip()
    Lev_Ratio, Fuzz_Ratio = lev.ratio(primary,secondary), fuzz.ratio(primary,secondary)
    Fuzz_Ratio_1 = fuzz.ratio(primary,secondary)
    match = fuzzymatch.single_compare(primary,secondary)
    Partial_Ratio, Token_Ratio = fuzz.partial_ratio(primary,secondary), fuzz.token_sort_ratio(primary,secondary)
    Token_Set_Ratio = fuzz.token_set_ratio(primary,secondary)
    primary_list, secondary_list = primary.split(), secondary.split()
    print(Lev_Ratio, Fuzz_Ratio, Fuzz_Ratio_1, match, Partial_Ratio, Token_Ratio, Token_Set_Ratio)

    arr = []
    word_match = False
    letter_match = False

    for n in primary_list:
        if len(n) == 1:
            arr.append(n)

    for a in arr:
        for b in secondary_list:
            if b.startswith(a):
                letter_match = True

    for n in secondary_list:
        if len(n) == 1:
            arr.append(n)

    for a in arr:
        for b in primary_list:
            if b.startswith(a):
                letter_match = True

    print(letter_match, word_match)
    if 'Match' == match or Lev_Ratio >= 0.75 or Fuzz_Ratio >= 80 or \
            Partial_Ratio >= 75 or Token_Ratio >= 80 or Token_Set_Ratio >= 80:
        results['True'] += 1
        print('True')
        print()

    elif Lev_Ratio >= 0.75 or Fuzz_Ratio >= 80 or \
            Partial_Ratio >= 75 or Token_Ratio >= 80 or Token_Set_Ratio >= 80:
        results['True'] += 1
        print('True')
        print()

    elif set(primary_list) & set(secondary_list):
        results['True'] += 1
        print('True')
        print()

    # elif letter_match
    else:
        results['False'] += 1
        print('False')
        print()

print('Total', results['True'] + results['False'])
print('Match ', results['True'])
print('Not Match', results['False'])
