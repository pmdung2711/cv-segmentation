import React from 'react';
import { Tabs, TabList, TabPanels, Tab, TabPanel, VStack, HStack, Badge, Text, Box, IconButton, StackDivider, Spacer } from '@chakra-ui/react'
import { FaBox } from 'react-icons/fa';
import { FaTrash } from 'react-icons/fa';
import PersonalInformation from './PersonalInformation';

function Resume({ resume, deleteResume }) {

    if (Object.keys(resume.data).length === 0) {
        return (
            <VStack >

            </VStack>

        )
    }

    const data = resume.data

    return (
        <VStack
            borderColor="gray.100"
            borderWidth="2px"
            p="4"
            borderRadius="lg"
            w="100%"
            maxW={{ base: '90vw', sm: '80vw', lg: '60vw', xl: '50vw' }}
            backgroundColor="white"
            alignSelf="start"

        >
            <Tabs align="start" variant='soft-rounded' colorScheme='orange'>
                <TabList>
                    <Tab>Resume Information</Tab>
                    <Tab>Raw Passages</Tab>
                    <Spacer />
                    <IconButton icon={<FaTrash />}
                        isRound='true'
                        onClick={() => deleteResume()} />
                </TabList>
                <TabPanels>
                    <TabPanel>
                        <PersonalInformation resume={resume} />
                    </TabPanel>
                    <TabPanel>
                        {data.passage_block.map(block => (
                            <Box p="4"
                                borderColor="gray.200"
                                borderWidth="2px"
                                borderRadius="lg"
                                key={block["block_id"]}>
                                <Badge mb="3" >
                                    {block['header']}
                                </Badge>
                                <Text>{block['content']}</Text>
                            </Box>
                        ))}
                    </TabPanel>
                </TabPanels>
            </Tabs>
        </VStack>);
}

export default Resume;