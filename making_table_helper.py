import os
import math
import json


def write_to_file(contents, path):
    with open(path, 'w') as f:
        f.write(contents)

def read_from_file(path):
    with open(path) as f:
        return ''.join(f.readlines())
    
    
def get_str_from_json(data):
    json_string = json.dumps(data)
    return json_string

def get_json_from_str(json_string):
    data = json.loads(json_string)
    return data


        
        
        
        

def get_pattern_to_gas_cost():

    gas_cost_of_patterns = [l for l in read_from_file('./data_replication_package/evaluation_statistics/gas_cost_of_patterns.txt').split('\n') if l != '']
    # gas_cost_of_patterns = gas_cost_of_patterns[gas_cost_of_patterns.index('<CONTENT_BEGINNING>')+1:]
    pattern_to_stats_d = dict()

    pattern_names_only = [i for i in gas_cost_of_patterns if '.' in i[:4]]
    cur_ind = 0
    count = 1
    for st in pattern_names_only[1:]:
        new_ind = gas_cost_of_patterns.index(st)
        pattern_to_stats_d[count] = gas_cost_of_patterns[cur_ind: new_ind]
        cur_ind = new_ind
        count += 1
    pattern_to_stats_d[count] = gas_cost_of_patterns[cur_ind: ]

    for c in pattern_to_stats_d:
        info_str = pattern_to_stats_d[c]
        assert info_str[1].startswith('**********************')
        assert info_str[6].startswith('**********************')



    new_pattern_to_stats_d = dict()

    for i in pattern_to_stats_d:
        d = dict()
        new_pattern_to_stats_d[i] = d

        first_4_lines = pattern_to_stats_d[i][2:6]
        d["deployment_transaction_before"] = first_4_lines[0].split(':')[1].strip().split(',')[0].strip()
        d["deployment_execution_before"] = first_4_lines[1].split(':')[1].strip().split(',')[0].strip()
        d["message_call_transaction_before"] = first_4_lines[2].split(':')[1].strip().split(',')[0].strip()
        d["message_call_execution_before"] = first_4_lines[3].split(':')[1].strip().split(',')[0].strip()

        d["deployment_transaction_after"] = first_4_lines[0].split(':')[1].strip().split(',')[1].strip()
        d["deployment_execution_after"] = first_4_lines[1].split(':')[1].strip().split(',')[1].strip()
        d["message_call_transaction_after"] = first_4_lines[2].split(':')[1].strip().split(',')[1].strip()
        d["message_call_execution_after"] = first_4_lines[3].split(':')[1].strip().split(',')[1].strip()


    pattern_to_gas_cost = new_pattern_to_stats_d
    return pattern_to_gas_cost

        
        
        
def make_regular_table():
    # regular
    cur_file_path = "./data_replication_package/evaluation_statistics/regular_results.txt"
    full_table_text = read_from_file(cur_file_path)


    data_entry_rows = [i for i in full_table_text.split('\n') if '&' in i]
    round_to_item_dict = dict()

    for r in data_entry_rows:
        if r.strip() == '':
            continue
        items = [i.strip() for i in r.split('&') if i.strip()!='']
        print(items)
        assert len(items) == 3

        pattern_name = items[0].strip()
        round_num = items[1].strip().split('.')[0]
        contract_num = items[1].strip().split('.')[1]
        verification_category = items[2].strip()

        cur_l = round_to_item_dict.get(round_num, [])
        cur_l.append((pattern_name, contract_num, verification_category))

        round_to_item_dict[round_num] = cur_l

        
        
        
    round_to_stats_dict = dict()
    max_dict = dict()
    cols = ['pass_rate', 'num_reported_patterns', 'num_reported_patterns_passed', 'num_reported_patterns_failed',
            'num_pattern_categories', 'num_failure_categories', 
             'pattern_entropy', 'failure_entropy', 'avg_num_lines', 'frac_valid_contracts', 'num_passed_patterns']

    cols = ['pass_rate', 'fail_rate', 'num_passed_patterns', 'num_reported_patterns',
           'num_pattern_categories', 'num_failure_categories',
           'pattern_entropy', 'failure_entropy', 'avg_num_lines', 'frac_valid_contracts']


    for round_num in round_to_item_dict:
        cur_d = dict()
        num_passed = 0
        num_failed = 0
        set_contracts_with_valid_patterns = set()
        set_all_contracts = set()
        pattern_categories = []
        failure_categories = []

        for item in round_to_item_dict[round_num]:
            pattern_name, contract_num, verification_category = item

            set_all_contracts.add(contract_num)
            if not verification_category.startswith('A'):
                num_passed += 1
                set_contracts_with_valid_patterns.add(contract_num)
            elif verification_category.startswith('A'):
                num_failed += 1
            else:
                print(item)
                raise Exception()
            if verification_category.startswith('A'):
                failure_categories.append(verification_category)
            else:
                pattern_categories.append(verification_category)
        cur_d['pass_rate'] = num_passed / (num_passed + num_failed)
        cur_d['fail_rate'] = num_failed / (num_passed + num_failed)
        cur_d['num_pattern_categories'] = len(set(pattern_categories))
        cur_d['num_failure_categories'] = len(set(failure_categories))
        cur_d['num_passed_patterns'] = len(pattern_categories)
        cur_d['num_failuer_patterns'] = len(failure_categories)
        cur_d['num_reported_patterns'] = len(pattern_categories) + len(failure_categories)
    #     cur_d['num_reported_patterns_passed'] = len(pattern_categories) / (len(pattern_categories) + len(failure_categories))
    #     cur_d['num_reported_patterns_failed'] = len(failure_categories) / (len(pattern_categories) + len(failure_categories))

    #     assert cur_d['pass_rate'] == cur_d['num_reported_patterns_passed']

        cur_d['frac_valid_contracts'] = len(set_contracts_with_valid_patterns) / len(set_all_contracts)

        print(set_contracts_with_valid_patterns)

        entropy_dict = dict()
        for p in pattern_categories:
            cur_c = entropy_dict.get(p, 0)
            entropy_dict[p] = cur_c + 1
        pattern_entropy = 0
        total_length_to_divide_by = len(pattern_categories)
        for p in entropy_dict:
            p_i = entropy_dict[p] / total_length_to_divide_by
            pattern_entropy -= p_i * math.log2(p_i)

        cur_d['pattern_entropy'] = pattern_entropy


        entropy_dict = dict()
        for p in failure_categories:
            cur_c = entropy_dict.get(p, 0)
            entropy_dict[p] = cur_c + 1
        failure_entropy = 0
        total_length_to_divide_by = len(failure_categories)
        for p in entropy_dict:
            p_i = entropy_dict[p] / total_length_to_divide_by
            failure_entropy -= p_i * math.log2(p_i)

        cur_d['failure_entropy'] = failure_entropy



        round_to_stats_dict[round_num] = cur_d



        for c in cols:
            if c == 'avg_num_lines':
                continue
            if c not in max_dict:
                max_dict[c] = cur_d[c]
            else:
                max_dict[c] = max([cur_d[c], max_dict[c]])


    t_l = []
    for cur_num in range(1,len(round_to_item_dict) + 1):
        l = []
        cur_round_prefix = f'./data_replication_package/GPT_inputs_outputs/main/round_{cur_num}/'
        for f in os.listdir(cur_round_prefix):
            if not f.endswith('.txt'):
                continue
            f = cur_round_prefix + f
            l.append(len(read_from_file(f).split('\n')))

        round_to_stats_dict[str(cur_num)]['avg_num_lines'] = sum(l) / len(l)
        t_l.append(sum(l) / len(l))
    max_dict['avg_num_lines'] = max(t_l)



    # to print regular stats

    contents = ''
    cols = ['pass_rate', 'num_reported_patterns_failed', 'num_passed_patterns', 'num_reported_patterns',
            'num_pattern_categories', 'num_failure_categories', 
             'pattern_entropy', 'failure_entropy', 'avg_num_lines', 'frac_valid_contracts']


    cols = ['pass_rate', 'fail_rate', 'num_passed_patterns', 'num_reported_patterns',
           'num_pattern_categories', 'num_failure_categories',
           'pattern_entropy', 'failure_entropy', 'avg_num_lines', 'frac_valid_contracts']

    for i in round_to_stats_dict:
        cur_row = str(i) + ' ' * 3 + '&'
        for c in cols:
            s = round_to_stats_dict[i][c]        
            if type(s) == float:
                new_s = round(s, 3)
            else:
                new_s = s
            if s == max_dict[c]:
                new_s = '\\textbf{' + str(new_s) + '}'

            cur_row += ' ' * 3  + str(new_s) + ' ' * 3
            if c == cols[-1]:
                cur_row += '\\\\' + '\n'
            else:
                cur_row += '&'
        contents += cur_row

    print(contents)
    
    
    
    
def make_ablation_table():


    # ablation
    cur_file_path = "./data_replication_package/evaluation_statistics/ablation_results.txt"
    full_table_text = read_from_file(cur_file_path)


    ablation_name_to_round_num_dict = dict()
    ablations = ['original', 'fse', 'codes', 'cot', 'sr']
    for i in range(len(ablations)):
        ablation_name_to_round_num_dict[ablations[i]] = str(i+1)


    data_entry_rows = [i for i in full_table_text.split('\n') if '&' in i]
    round_to_item_dict = dict()

    for r in data_entry_rows:
        if r.strip() == '':
            continue
        items = [i.strip() for i in r.split('&') if i.strip()!='']
        print(items)
        assert len(items) == 3

        pattern_name = items[0].strip()
        round_num = items[1].strip().split('.')[0]
        sub_round_num = items[1].strip().split('.')[1]
        contract_num = items[1].strip().split('.')[2]
        verification_category = items[2].strip()

        round_num = ablation_name_to_round_num_dict[round_num]
        contract_num = sub_round_num + '.' + contract_num

        cur_l = round_to_item_dict.get(round_num, [])
        cur_l.append((pattern_name, contract_num, verification_category))
        round_to_item_dict[round_num] = cur_l




    cols = ['pass_rate', 'num_reported_patterns', 'num_reported_patterns_passed', 'num_reported_patterns_failed',
            'num_pattern_categories', 'num_failure_categories', 
             'pattern_entropy', 'failure_entropy', 'avg_num_lines', 'frac_valid_contracts', 'num_passed_patterns']

    cols = ['pass_rate', 'fail_rate', 'num_passed_patterns', 'num_reported_patterns',
           'num_pattern_categories', 'num_failure_categories',
           'pattern_entropy', 'failure_entropy', 'avg_num_lines', 'frac_valid_contracts']

    for cur_pattern_round_num in ['7', '8']:
        round_to_stats_dict = dict()
        max_dict = dict()
        for round_num in round_to_item_dict:
            cur_d = dict()
            num_passed = 0
            num_failed = 0
            set_contracts_with_valid_patterns = set()
            set_all_contracts = set()
            pattern_categories = []
            failure_categories = []

            for item in round_to_item_dict[round_num]:
                pattern_name, contract_num, verification_category = item

                if not contract_num.startswith(cur_pattern_round_num):
                    continue
                contract_num = contract_num.split('.')[1]

                set_all_contracts.add(contract_num)
                if not verification_category.startswith('A'):
                    num_passed += 1
                    set_contracts_with_valid_patterns.add(contract_num)
                elif verification_category.startswith('A'):
                    num_failed += 1
                else:
                    print(item)
                    raise Exception()
                if verification_category.startswith('A'):
                    failure_categories.append(verification_category)
                else:
                    pattern_categories.append(verification_category)
            cur_d['pass_rate'] = num_passed / (num_passed + num_failed)
            cur_d['fail_rate'] = num_failed / (num_passed + num_failed)
            cur_d['num_pattern_categories'] = len(set(pattern_categories))
            cur_d['num_failure_categories'] = len(set(failure_categories))
            cur_d['num_passed_patterns'] = len(pattern_categories)
            cur_d['num_failuer_patterns'] = len(failure_categories)
            cur_d['num_reported_patterns'] = len(pattern_categories) + len(failure_categories)
        #     cur_d['num_reported_patterns_passed'] = len(pattern_categories) / (len(pattern_categories) + len(failure_categories))
        #     cur_d['num_reported_patterns_failed'] = len(failure_categories) / (len(pattern_categories) + len(failure_categories))

        #     assert cur_d['pass_rate'] == cur_d['num_reported_patterns_passed']

            print(len(set_contracts_with_valid_patterns), len(set_all_contracts))
            cur_d['frac_valid_contracts'] = len(set_contracts_with_valid_patterns) / len(set_all_contracts)

        #     print(set_contracts_with_valid_patterns)

            entropy_dict = dict()
            for p in pattern_categories:
                cur_c = entropy_dict.get(p, 0)
                entropy_dict[p] = cur_c + 1
            pattern_entropy = 0
            total_length_to_divide_by = len(pattern_categories)
            for p in entropy_dict:
                p_i = entropy_dict[p] / total_length_to_divide_by
                pattern_entropy -= p_i * math.log2(p_i)

            cur_d['pattern_entropy'] = pattern_entropy


            entropy_dict = dict()
            for p in failure_categories:
                cur_c = entropy_dict.get(p, 0)
                entropy_dict[p] = cur_c + 1
            failure_entropy = 0
            total_length_to_divide_by = len(failure_categories)
            for p in entropy_dict:
                p_i = entropy_dict[p] / total_length_to_divide_by
                failure_entropy -= p_i * math.log2(p_i)

            cur_d['failure_entropy'] = failure_entropy



            round_to_stats_dict[round_num] = cur_d



            for c in cols:
                if c == 'avg_num_lines':
                    continue
                if c not in max_dict:
                    max_dict[c] = cur_d[c]
                else:
                    max_dict[c] = max([cur_d[c], max_dict[c]])






        t_l = []
        for cur_num in range(1,6):
            num_to_name = {1: 'original', 2: 'fse', 3: 'codes', 4: 'cot', 5: 'si'}
            name = num_to_name[cur_num]
            l = []

            cur_round_prefix = f'./data_replication_package/GPT_inputs_outputs/ablation/{name}/{cur_pattern_round_num}/'
            for f in os.listdir(cur_round_prefix):
                if not f.endswith('.txt'):
                    continue
                f = cur_round_prefix + f
                l.append(len(read_from_file(f).split('\n')))

            round_to_stats_dict[str(cur_num)]['avg_num_lines'] = sum(l) / len(l)
            t_l.append(sum(l) / len(l))
        max_dict['avg_num_lines'] = max(t_l)






        # to print ablation stats

        contents = ''

        cols = ['pass_rate', 'fail_rate', 'num_passed_patterns', 'num_reported_patterns',
               'num_pattern_categories', 'num_failure_categories',
               'pattern_entropy', 'failure_entropy', 'avg_num_lines', 'frac_valid_contracts']

        order = ['1', '4', '2', '3', '5']
        type_num_to_prefix = dict()
        type_num_to_prefix['1'] = '$\\checkmark$   &  $\\checkmark$  &$\\checkmark$   &$\\checkmark$'
        type_num_to_prefix['4'] = '$\\times$   &  $\\checkmark$  &$\\checkmark$   &$\\checkmark$'
        type_num_to_prefix['2'] = '$\\checkmark$   &  $\\times$  &$\\checkmark$   &$\\checkmark$'
        type_num_to_prefix['3'] = '$\\checkmark$   &  $\\checkmark$  &$\\times$   &$\\checkmark$'
        type_num_to_prefix['5'] = '$\\checkmark$   &  $\\checkmark$  &$\\checkmark$   &$\\times$'


        for i in order:
            cur_row = type_num_to_prefix[i] + ' ' * 3 + '&'
            for c in cols:
                s = round_to_stats_dict[i][c]        
                if type(s) == float:
                    new_s = round(s, 3)
                else:
                    new_s = s
                if s == max_dict[c]:
                    new_s = '\\textbf{' + str(new_s) + '}'

                cur_row += ' ' * 3  + str(new_s) + ' ' * 3
                if c == cols[-1]:
                    cur_row += '\\\\' + '\n'
                else:
                    cur_row += '&'
            contents += cur_row + '\n\n'

        print(contents)    
        print('-----------------')








    round_to_stats_dict = dict()
    max_dict = dict()   
    for round_num in round_to_item_dict:
        cur_d = dict()
        num_passed = 0
        num_failed = 0
        set_contracts_with_valid_patterns = set()
        set_all_contracts = set()
        pattern_categories = []
        failure_categories = []

        for item in round_to_item_dict[round_num]:
            pattern_name, contract_num, verification_category = item


            set_all_contracts.add(contract_num)
            if not verification_category.startswith('A'):
                num_passed += 1
                set_contracts_with_valid_patterns.add(contract_num)
            elif verification_category.startswith('A'):
                num_failed += 1
            else:
                print(item)
                raise Exception()
            if verification_category.startswith('A'):
                failure_categories.append(verification_category)
            else:
                pattern_categories.append(verification_category)
        cur_d['pass_rate'] = num_passed / (num_passed + num_failed)
        cur_d['fail_rate'] = num_failed / (num_passed + num_failed)
        cur_d['num_pattern_categories'] = len(set(pattern_categories))
        cur_d['num_failure_categories'] = len(set(failure_categories))
        cur_d['num_passed_patterns'] = len(pattern_categories)
        cur_d['num_failuer_patterns'] = len(failure_categories)
        cur_d['num_reported_patterns'] = len(pattern_categories) + len(failure_categories)
    #     cur_d['num_reported_patterns_passed'] = len(pattern_categories) / (len(pattern_categories) + len(failure_categories))
    #     cur_d['num_reported_patterns_failed'] = len(failure_categories) / (len(pattern_categories) + len(failure_categories))

    #     assert cur_d['pass_rate'] == cur_d['num_reported_patterns_passed']

        print(len(set_contracts_with_valid_patterns), len(set_all_contracts))
        cur_d['frac_valid_contracts'] = len(set_contracts_with_valid_patterns) / len(set_all_contracts)

    #     print(set_contracts_with_valid_patterns)

        entropy_dict = dict()
        for p in pattern_categories:
            cur_c = entropy_dict.get(p, 0)
            entropy_dict[p] = cur_c + 1
        pattern_entropy = 0
        total_length_to_divide_by = len(pattern_categories)
        for p in entropy_dict:
            p_i = entropy_dict[p] / total_length_to_divide_by
            pattern_entropy -= p_i * math.log2(p_i)

        cur_d['pattern_entropy'] = pattern_entropy


        entropy_dict = dict()
        for p in failure_categories:
            cur_c = entropy_dict.get(p, 0)
            entropy_dict[p] = cur_c + 1
        failure_entropy = 0
        total_length_to_divide_by = len(failure_categories)
        for p in entropy_dict:
            p_i = entropy_dict[p] / total_length_to_divide_by
            failure_entropy -= p_i * math.log2(p_i)

        cur_d['failure_entropy'] = failure_entropy



        round_to_stats_dict[round_num] = cur_d



        for c in cols:
            if c == 'avg_num_lines':
                continue
            if c not in max_dict:
                max_dict[c] = cur_d[c]
            else:
                max_dict[c] = max([cur_d[c], max_dict[c]])





    #     for cur_pattern_round_num in ['7', '8']:

    t_l = []
    for cur_num in range(1,6):
        num_to_name = {1: 'original', 2: 'fse', 3: 'codes', 4: 'cot', 5: 'si'}
        name = num_to_name[cur_num]
        l = []


        cur_round_prefix_7 = f'./data_replication_package/GPT_inputs_outputs/ablation/{name}/{7}/'
        cur_round_prefix_8 = f'./data_replication_package/GPT_inputs_outputs/ablation/{name}/{8}/'

        for f in os.listdir(cur_round_prefix_7):
            if not f.endswith('.txt'):
                continue
            f = cur_round_prefix_7 + f
            l.append(len(read_from_file(f).split('\n')))

        for f in os.listdir(cur_round_prefix_8):
            if not f.endswith('.txt'):
                continue
            f = cur_round_prefix_8 + f
            l.append(len(read_from_file(f).split('\n')))

        round_to_stats_dict[str(cur_num)]['avg_num_lines'] = sum(l) / len(l)
        t_l.append(sum(l) / len(l))
    max_dict['avg_num_lines'] = max(t_l)






    # to print ablation stats

    contents = ''

    cols = ['pass_rate', 'fail_rate', 'num_passed_patterns', 'num_reported_patterns',
           'num_pattern_categories', 'num_failure_categories',
           'pattern_entropy', 'failure_entropy', 'avg_num_lines', 'frac_valid_contracts']

    order = ['1', '4', '2', '3', '5']
    type_num_to_prefix = dict()
    type_num_to_prefix['1'] = '$\\checkmark$   &  $\\checkmark$  &$\\checkmark$   &$\\checkmark$'
    type_num_to_prefix['4'] = '$\\times$   &  $\\checkmark$  &$\\checkmark$   &$\\checkmark$'
    type_num_to_prefix['2'] = '$\\checkmark$   &  $\\times$  &$\\checkmark$   &$\\checkmark$'
    type_num_to_prefix['3'] = '$\\checkmark$   &  $\\checkmark$  &$\\times$   &$\\checkmark$'
    type_num_to_prefix['5'] = '$\\checkmark$   &  $\\checkmark$  &$\\checkmark$   &$\\times$'


    for i in order:
        cur_row = type_num_to_prefix[i] + ' ' * 3 + '&'
        for c in cols:
            s = round_to_stats_dict[i][c]        
            if type(s) == float:
                new_s = round(s, 3)
            else:
                new_s = s
            if s == max_dict[c]:
                new_s = '\\textbf{' + str(new_s) + '}'

            cur_row += ' ' * 3  + str(new_s) + ' ' * 3
            if c == cols[-1]:
                cur_row += '\\\\' + '\n'
            else:
                cur_row += '&'
        contents += cur_row + '\n\n'

    print(contents)    
    print('-----------------')


def make_claude_table():

    # Claude
    cur_file_path = './exp_5 Another LLM/new_round_results/template_results.txt'
    full_table_text = read_from_file(cur_file_path)


    data_entry_rows = [i for i in full_table_text.split('\n') if '&' in i]
    round_to_item_dict = dict()

    for r in data_entry_rows:
        if r.strip() == '':
            continue
        items = [i.strip() for i in r.split('&') if i.strip()!='']
        print(items)
        assert len(items) == 3 or len(items) == 4

        if all([i.strip() == '' for i in items]):
            continue

        pattern_name = items[0].strip()
        round_num = items[1].strip().split('.')[0]
        contract_num = items[1].strip().split('.')[1]
        verification_category = items[2].strip()

        cur_l = round_to_item_dict.get(round_num, [])
        cur_l.append((pattern_name, contract_num, verification_category))

        round_to_item_dict[round_num] = cur_l




    round_to_stats_dict = dict()
    max_dict = dict()
    cols = ['pass_rate', 'num_reported_patterns', 'num_reported_patterns_passed', 'num_reported_patterns_failed',
            'num_pattern_categories', 'num_failure_categories', 
             'pattern_entropy', 'failure_entropy', 'avg_num_lines', 'frac_valid_contracts', 'num_passed_patterns']

    cols = ['pass_rate', 'fail_rate', 'num_passed_patterns', 'num_reported_patterns',
           'num_pattern_categories', 'num_failure_categories',
           'pattern_entropy', 'failure_entropy', 'avg_num_lines', 'frac_valid_contracts']


    for round_num in round_to_item_dict:
        cur_d = dict()
        num_passed = 0
        num_failed = 0
        set_contracts_with_valid_patterns = set()
        set_all_contracts = set()
        pattern_categories = []
        failure_categories = []

        for item in round_to_item_dict[round_num]:
            pattern_name, contract_num, verification_category = item

            set_all_contracts.add(contract_num)
            if not verification_category.startswith('A'):
                num_passed += 1
                set_contracts_with_valid_patterns.add(contract_num)
            elif verification_category.startswith('A'):
                num_failed += 1
            else:
                print(item)
                raise Exception()
            if verification_category.startswith('A'):
                failure_categories.append(verification_category)
            else:
                pattern_categories.append(verification_category)
        cur_d['pass_rate'] = num_passed / (num_passed + num_failed)
        cur_d['fail_rate'] = num_failed / (num_passed + num_failed)
        cur_d['num_pattern_categories'] = len(set(pattern_categories))
        cur_d['num_failure_categories'] = len(set(failure_categories))
        cur_d['num_passed_patterns'] = len(pattern_categories)
        cur_d['num_failuer_patterns'] = len(failure_categories)
        cur_d['num_reported_patterns'] = len(pattern_categories) + len(failure_categories)
    #     cur_d['num_reported_patterns_passed'] = len(pattern_categories) / (len(pattern_categories) + len(failure_categories))
    #     cur_d['num_reported_patterns_failed'] = len(failure_categories) / (len(pattern_categories) + len(failure_categories))

    #     assert cur_d['pass_rate'] == cur_d['num_reported_patterns_passed']

        cur_d['frac_valid_contracts'] = len(set_contracts_with_valid_patterns) / len(set_all_contracts)

        print(set_contracts_with_valid_patterns)

        entropy_dict = dict()
        for p in pattern_categories:
            cur_c = entropy_dict.get(p, 0)
            entropy_dict[p] = cur_c + 1
        pattern_entropy = 0
        total_length_to_divide_by = len(pattern_categories)
        for p in entropy_dict:
            p_i = entropy_dict[p] / total_length_to_divide_by
            pattern_entropy -= p_i * math.log2(p_i)

        cur_d['pattern_entropy'] = pattern_entropy


        entropy_dict = dict()
        for p in failure_categories:
            cur_c = entropy_dict.get(p, 0)
            entropy_dict[p] = cur_c + 1
        failure_entropy = 0
        total_length_to_divide_by = len(failure_categories)
        for p in entropy_dict:
            p_i = entropy_dict[p] / total_length_to_divide_by
            failure_entropy -= p_i * math.log2(p_i)

        cur_d['failure_entropy'] = failure_entropy



        round_to_stats_dict[round_num] = cur_d



        for c in cols:
            if c == 'avg_num_lines':
                continue
            if c not in max_dict:
                max_dict[c] = cur_d[c]
            else:
                max_dict[c] = max([cur_d[c], max_dict[c]])


    t_l = []
    for cur_num in range(1,len(round_to_item_dict) + 1):
        l = []
        cur_round_prefix = f'./data_replication_package/GPT_inputs_outputs/main/round_{cur_num}/'
        for f in os.listdir(cur_round_prefix):
            if not f.endswith('.txt'):
                continue
            f = cur_round_prefix + f
            l.append(len(read_from_file(f).split('\n')))

        round_to_stats_dict[str(cur_num)]['avg_num_lines'] = sum(l) / len(l)
        t_l.append(sum(l) / len(l))
    max_dict['avg_num_lines'] = max(t_l)



    # to print regular stats

    contents = ''
    cols = ['pass_rate', 'num_reported_patterns_failed', 'num_passed_patterns', 'num_reported_patterns',
            'num_pattern_categories', 'num_failure_categories', 
             'pattern_entropy', 'failure_entropy', 'avg_num_lines', 'frac_valid_contracts']


    cols = ['pass_rate', 'fail_rate', 'num_passed_patterns', 'num_reported_patterns',
           'num_pattern_categories', 'num_failure_categories',
           'pattern_entropy', 'failure_entropy', 'avg_num_lines', 'frac_valid_contracts']

    for i in round_to_stats_dict:
        cur_row = str(i) + ' ' * 3 + '&'
        for c in cols:
            s = round_to_stats_dict[i][c]        
            if type(s) == float:
                new_s = round(s, 3)
            else:
                new_s = s
            if s == max_dict[c]:
                new_s = '\\textbf{' + str(new_s) + '}'

            cur_row += ' ' * 3  + str(new_s) + ' ' * 3
            if c == cols[-1]:
                cur_row += '\\\\' + '\n'
            else:
                cur_row += '&'
        contents += cur_row

    print(contents)



    
    
    
def make_vyper_table():

    # vyper
    cur_file_path = './exp_1 vyper/new_round_results/template_results.txt'
    full_table_text = read_from_file(cur_file_path)


    data_entry_rows = [i for i in full_table_text.split('\n') if '&' in i]
    round_to_item_dict = dict()

    for r in data_entry_rows:
        if r.strip() == '':
            continue
        items = [i.strip() for i in r.split('&') if i.strip()!='']
        if len(items) == 1:
            assert '.' in items[0]
            continue
        print(items)
        assert len(items) == 3 or len(items) == 4

        if all([i.strip() == '' for i in items]):
            continue

        pattern_name = items[0].strip()
        round_num = items[1].strip().split('.')[0]
        contract_num = items[1].strip().split('.')[1]
        verification_category = items[2].strip()

        cur_l = round_to_item_dict.get(round_num, [])
        cur_l.append((pattern_name, contract_num, verification_category))

        round_to_item_dict[round_num] = cur_l




    round_to_stats_dict = dict()
    max_dict = dict()
    cols = ['pass_rate', 'num_reported_patterns', 'num_reported_patterns_passed', 'num_reported_patterns_failed',
            'num_pattern_categories', 'num_failure_categories', 
             'pattern_entropy', 'failure_entropy', 'avg_num_lines', 'frac_valid_contracts', 'num_passed_patterns']

    cols = ['pass_rate', 'fail_rate', 'num_passed_patterns', 'num_reported_patterns',
           'num_pattern_categories', 'num_failure_categories',
           'pattern_entropy', 'failure_entropy', 'avg_num_lines', 'frac_valid_contracts']



    cur_d = dict()
    num_passed = 0
    num_failed = 0
    set_contracts_with_valid_patterns = set()
    set_all_contracts = set()
    pattern_categories = []
    failure_categories = []
        
        
    for round_num in round_to_item_dict:
        

        for item in round_to_item_dict[round_num]:
            pattern_name, contract_num, verification_category = item

            set_all_contracts.add(contract_num)
            if not verification_category.startswith('A'):
                num_passed += 1
                set_contracts_with_valid_patterns.add(contract_num)
            elif verification_category.startswith('A'):
                num_failed += 1
            else:
                print(item)
                raise Exception()
            if verification_category.startswith('A'):
                failure_categories.append(verification_category)
            else:
                pattern_categories.append(verification_category)
    cur_d['pass_rate'] = num_passed / (num_passed + num_failed)
    cur_d['fail_rate'] = num_failed / (num_passed + num_failed)
    cur_d['num_pattern_categories'] = len(set(pattern_categories))
    cur_d['num_failure_categories'] = len(set(failure_categories))
    cur_d['num_passed_patterns'] = len(pattern_categories)
    cur_d['num_failuer_patterns'] = len(failure_categories)
    cur_d['num_reported_patterns'] = len(pattern_categories) + len(failure_categories)
    #     cur_d['num_reported_patterns_passed'] = len(pattern_categories) / (len(pattern_categories) + len(failure_categories))
    #     cur_d['num_reported_patterns_failed'] = len(failure_categories) / (len(pattern_categories) + len(failure_categories))

    #     assert cur_d['pass_rate'] == cur_d['num_reported_patterns_passed']

    cur_d['frac_valid_contracts'] = len(set_contracts_with_valid_patterns) / len(set_all_contracts)


    entropy_dict = dict()
    for p in pattern_categories:
        cur_c = entropy_dict.get(p, 0)
        entropy_dict[p] = cur_c + 1
    pattern_entropy = 0
    total_length_to_divide_by = len(pattern_categories)
    for p in entropy_dict:
        p_i = entropy_dict[p] / total_length_to_divide_by
        pattern_entropy -= p_i * math.log2(p_i)

    cur_d['pattern_entropy'] = pattern_entropy


    entropy_dict = dict()
    for p in failure_categories:
        cur_c = entropy_dict.get(p, 0)
        entropy_dict[p] = cur_c + 1
    failure_entropy = 0
    total_length_to_divide_by = len(failure_categories)
    for p in entropy_dict:
        p_i = entropy_dict[p] / total_length_to_divide_by
        failure_entropy -= p_i * math.log2(p_i)

    cur_d['failure_entropy'] = failure_entropy




#     t_l = []
#     for cur_num in range(1,len(round_to_item_dict) + 1):
#         l = []
#         cur_round_prefix = f'./data_replication_package/GPT_inputs_outputs/regular/round_{cur_num}/'
#         for f in os.listdir(cur_round_prefix):
#             if not f.endswith('.txt'):
#                 continue
#             f = cur_round_prefix + f
#             l.append(len(read_from_file(f).split('\n')))

#         round_to_stats_dict[str(cur_num)]['avg_num_lines'] = sum(l) / len(l)
#         t_l.append(sum(l) / len(l))
#     max_dict['avg_num_lines'] = max(t_l)

    print(cur_d)
    print('num_passed: ', num_passed)
    print('num_failed: ', num_failed)
    print('set_contracts_with_valid_patterns: ', set_contracts_with_valid_patterns)
    print('set_all_contracts: ', set_all_contracts)
    print('pattern_categories: ', pattern_categories)
    print('failure_categories: ', failure_categories)

        
def counting_claude_time():

    # Claude
    cur_file_path = './exp_5 Another LLM/new_round_results/template_results.txt'
    full_table_text = read_from_file(cur_file_path)


    data_entry_rows = [i.strip() for i in full_table_text.split('\n') if i.strip().startswith('[')]
    all_in_seconds = []
    
    for r in data_entry_rows:
        r = r.strip('[')
        section, time_taken = r.split(']')
        
        round_num, contract_num = section.strip().split('.')
        round_num = round_num.strip()
        contract_num = contract_num.strip()
        
        min_taken, seconds_taken = time_taken.strip().split(':')
        
        cur_all_seconds = int(min_taken.strip()) * 60 + int(seconds_taken.strip())
        
        all_in_seconds.append(cur_all_seconds)
        
        print(f'at round {round_num} contract {contract_num}: min_taken {min_taken} and seconds_taken {seconds_taken}. In total {cur_all_seconds}')   
    
    return all_in_seconds
    
    