#====================================================================
#
# ECE 5775 Final Project
# MapReduce on FPGA: Accelerator for KNN Digit Recognition Algorithm
# 
# Instructor: Professor Zhang Zhiru 
# Authors:    Mengcheng Qi ( mq58  )
#             Xiao Tan     ( xt85  )
#             Hanjie Mei   ( hm492 )
# 
#====================================================================

#--------------------------------------------------------------------
# The Alternative Design Files: 
#--------------------------------------------------------------------
    
    digitrecPRTL.py                -- Top Level
    digitrecMsg.py                 -- digitrec message 
    digitrecPRTL_test.py           -- digitrecPRTL test file
    
    SchedulerPRTL.py               -- Scheduler
    
    MapperPRTL.py                  -- Mapper top level
    DistancePRTL.py                -- Mapper helper modules
    MapperPRTL_test.py             -- Mapper test file
    
    ReducerPRTL.py                 -- Reducer top level
    ReducerPRTL_test.py            -- Reducer test file
    
    MergerPRTL.py                  -- Merger top level
    MergerPRTL_test.py             -- Merger test file
    
    FindMaxMin.py                  -- FindMaxMin helper modules
    FindMaxMin_test.py             -- FindMaxMin test file
    AdderTree.py                   -- AdderTree helper module
    AdderTree_test.py              -- AdderTree test file
    
    data/                          -- a folder contains test data 
                                      and training data files
    
    conftest.py                    -- py.test scripts
    pytest.ini                     -- py.test scripts
    
#--------------------------------------------------------------------
# Instructions to run the code
#--------------------------------------------------------------------

digitrecPRTL_test.py is the top level test file of our design.
You can change the following parameters at the top of this test file
to regenerate the evaluation results we listed in the report. 

    TEST_SIZE                      -- the total number of test data
    TRAIN_SIZE                     -- the number of training data per digit
    MAPPER_NUM                     -- the total number of mappers
    k                              -- k value

Default values:

    TEST_SIZE   = 180
    TRAIN_SIZE  = 1800
    MAPPER_NUM  = 30
    k           = 3

Setting value suggestions:

    TEST_SIZE should be an integer such that 180 is divisible by it. 
    TRAIN_SIZE should be divisible by the number of mappers per digit.
    The design supports k value equal to or larger than 2. 

The following commands illlustrate how to run our design by this test file.
It will print line trace, dump out final results and accuracy:

    py.test digitrecPRTL_test.py -s

Notes:

    When running the design with default parameter settings, it probably takes more than an hour.
    The baseline design codes can be found from our github repository within the folder: digitrec_gen


If you have any questions when running our design, please feel free to contact us.
Thank you for reading!



