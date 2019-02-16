""" 
    File Name:          UnoPytorch/launcher.py
    Author:             Xiaotian Duan (xduan7)
    Email:              xduan7@uchicago.edu
    Date:               8/17/18
    Python Version:     3.6.6
    File Description:   

"""

import sys
import runpy
import datetime

from utils.miscellaneous.tee import Tee

if __name__ == '__main__':

    param_dict_list = [

        # {'trn_src': ['GDSC'],
        #  'val_srcs': ['GDSC'], },

        # Training + validation data sources for the transfer learning matrix
        {'trn_src': ['NCI60'],
         'val_srcs': ['NCI60', 'CTRP', 'GDSC', 'CCLE', 'gCSI'], },

        {'trn_src': ['CTRP'],
         'val_srcs': ['NCI60', 'CTRP', 'GDSC', 'CCLE', 'gCSI'], },

        {'trn_src': ['GDSC'],
         'val_srcs': ['NCI60', 'CTRP', 'GDSC', 'CCLE', 'gCSI'], },

        {'trn_src': ['CCLE'],
         'val_srcs': ['NCI60', 'CTRP', 'GDSC', 'CCLE', 'gCSI'], },

        {'trn_src': ['gCSI'],
         'val_srcs': ['NCI60', 'CTRP', 'GDSC', 'CCLE', 'gCSI'], },
    ]

    # ['source_scale', 'combat', 'livermore']
    rnaseq_feature_list = ['source_scale', ]

    now = datetime.datetime.now()
    val_results_dir = './results/saved_predictions(%02d%02d_%02d%02d)/' \
        % (now.month, now.day, now.hour, now.minute)

    for rnaseq_feature in rnaseq_feature_list:
        for param_dict in param_dict_list:

            # Try until the models are successfully trained

            # module_finished = False
            # while not module_finished:

            now = datetime.datetime.now()

            # Save log with name = (training data source + time)
            tee = Tee('./results/logs/%s_(%02d%02d_%02d%02d).txt'
                      % (param_dict['trn_src'],
                         now.month, now.day, now.hour, now.minute))
            sys.stdout = tee

            sys.argv = [
                'uno_pytorch',

                # Dataset parameters ######################################
                # Training and validation data sources
                '--trn_src', *param_dict['trn_src'],
                '--val_srcs', *param_dict['val_srcs'],

                # Pre-processing for dataframes
                '--lat_scaling', 'none',
                '--grth_scaling', 'none',
                '--dscptr_scaling', 'std',
                '--rnaseq_scaling', 'std',
                '--dscptr_nan_threshold', '0.0',
                '--qed_scaling', 'none',

                # Feature usage and partitioning settings
                '--rnaseq_feature_usage', rnaseq_feature,
                '--drug_feature_usage', 'latent',
                '--validation_ratio', '0.2',
                # '--disjoint_drugs',
                '--disjoint_cells',

                # Network configuration ###################################
                # Encoders for drug features and RNA sequence
                '--gene_layer_dim', '1024',
                '--gene_num_layers', '2',
                '--gene_latent_dim', '512',

                '--drug_layer_dim', '4096',
                '--drug_num_layers', '2',
                '--drug_latent_dim', '1024',

                # Using autoencoder for drug/sequence encoder init
                '--autoencoder_init',

                # Drug response regression network
                '--resp_layer_dim', '2048',
                '--resp_num_layers_per_block', '2',
                '--resp_num_blocks', '4',
                '--resp_num_layers', '0',
                '--resp_dropout', '0.1',
                '--resp_activation', 'none',

                # Cell line classification network(s)
                # '--cl_clf_layer_dim', '256',
                # '--cl_clf_num_layers', '2',

                # Drug target family classification network
                # '--drug_target_layer_dim', '1024',
                # '--drug_target_num_layers', '2',

                # Drug weighted QED regression network
                # '--drug_qed_layer_dim', '1024',
                # '--drug_qed_num_layers', '2',
                # '--drug_qed_activation', 'sigmoid',

                # Training and validation parameters ######################
                # Drug response regression training parameters
                '--resp_loss_func', 'mse',
                '--resp_opt', 'SGD',
                '--resp_lr', '1e-5',

                # Drug response uncertainty quantification parameters
                # '--resp_uq',
                # '--resp_uq_dropout', '0.1',
                # '--resp_uq_length_scale', '0.01',
                # '--resp_uq_num_runs', '32',

                # Cell line classification training parameters
                # '--cl_clf_opt', 'SGD',
                # '--cl_clf_lr', '8e-3',

                # Drug target family classification training parameters
                # '--drug_target_opt', 'SGD',
                # '--drug_target_lr', '2e-3',

                # Drug weighted QED regression training parameters
                # '--drug_qed_loss_func', 'mse',
                # '--drug_qed_opt', 'SGD',
                # '--drug_qed_lr', '1e-2',

                # Starting epoch for drug response validation
                '--resp_val_start_epoch', '20',

                # Early stopping based on R2 score of drug response
                '--early_stop_patience', '5',

                # Global/shared training parameters
                '--l2_regularization', '1e-5',
                '--lr_decay_factor', '0.98',
                '--trn_batch_size', '32',
                '--val_batch_size', '256',
                '--max_num_batches', '1000',
                '--max_num_epochs', '1000',

                # Validation results directory
                '--val_results_dir', val_results_dir,

                # Miscellaneous settings ##################################
                # '--multi_gpu'
                # '--no_cuda'
                '--rand_state', '0', ]

            runpy.run_module('uno_pytorch')

            # module_finished = True
            # except Exception as e:
            #     print('Encountering Exception %s' % e)
            #     print('Re-initiate a new run ...')

            sys.stdout = tee.default_stdout()
