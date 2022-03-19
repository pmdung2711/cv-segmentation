import {
    VStack,
    useColorMode, Tabs, TabList, TabPanels, Tab, TabPanel, Input, Textarea
    , Modal,
    ModalOverlay,
    ModalContent,
    ModalBody,
    Spinner,
    Button, Text, useDisclosure, AlertDialog, Box, Badge,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogContent,
    AlertDialogOverlay,
    Stack,
    HStack
} from '@chakra-ui/react';
import ParseResume from './ParseResume';
import { useState, useEffect } from 'react'
import Resume from './Resume';
import React, { useRef } from 'react';
import { nanoid } from 'nanoid'
import axios, { post } from 'axios'

import sample_text from "./sample.js"

function Parser() {

    const [resume, setResume] = useState(
        () => JSON.parse(localStorage.getItem('resume_data')) || []
    );

    const [inputValue, setValue] = useState(sample_text)
    const [passages, setPasssages] = useState([])
    const onCloseDialog = () => setIsOpenDialog(false)
    const cancelRef = useRef()
    const { isOpen, onOpen, onClose } = useDisclosure()
    const [isOpenDialog, setIsOpenDialog] = React.useState(false)

    console.log(sample_text)

    function handleSubmit(e) {

        e.preventDefault()


        if (inputValue === "") {
            setIsOpenDialog(true)
        } else {
            const url = "http://127.0.0.1:8899/segmentation"
            onOpen()
            const body = {
                "dataset": "resume",
                "text": inputValue
            }
            axios({
                method: "post",
                url: url,
                data: body,
                headers: { "Content-Type": "application/json" },
            }).then(response => {
                setPasssages(response.data.passages)
                onClose()
            }).catch(error => {
                onClose()
            })
        }

    }
    useEffect(() => {
        localStorage.setItem('resume_data', JSON.stringify(resume))
    }, [resume])

    function addResume(resume) {
        console.log(resume)
        setResume(resume)
    }

    function handleInputChange(e) {
        const inputValue = e.target.value
        setValue(inputValue)
    }

    function deleteResume() {
        console.log("Remove Resume")
        setResume({
            data: {}
        })
        console.log("Resume:", resume)
    }

    const { colorMode, toggleColorMode } = useColorMode();


    return (
        <div>
            <Stack backgroundColor="red.50" p="10">
                <Tabs align="center" variant='soft-rounded' colorScheme='red'>
                    <TabList >
                        <Tab>Text Segmentation</Tab>
                        <Tab>Resume Parser</Tab>
                    </TabList>
                    <TabPanels>
                        <TabPanel>
                            <VStack
                                borderColor="gray.100"
                                borderWidth="2px"
                                p="4"
                                borderRadius="lg"
                                backgroundColor="#e8dcdc"
                                align="start"
                                w="100%"
                                style={{ height: "auto", width: "500px" }}
                                maxW={{ base: '90vw', sm: '80vw', lg: '60vw', xl: '50vw' }}
                                spacing="3"

                            >
                                <HStack >
                                    <Text alignSelf="center">
                                        Please type your text
                                    </Text>
                                </HStack>

                                <Textarea
                                    onChange={handleInputChange}
                                    value={inputValue}
                                    placeholder='Here is a sample placeholder'
                                    height="400px"
                                    backgroundColor="#fffafa"
                                    resize="none" />
                                <Button alignSelf="center" colorScheme="red" px="8" type="submit" onClick={(e) => handleSubmit(e)}>Split the text</Button>
                                <AlertDialog
                                    isOpen={isOpenDialog}
                                    leastDestructiveRef={cancelRef}
                                    onClose={onCloseDialog}
                                >
                                    <AlertDialogOverlay>
                                        <AlertDialogContent>
                                            <AlertDialogHeader fontSize='lg' fontWeight='bold'>
                                                The input is blank
                                            </AlertDialogHeader>
                                            <AlertDialogFooter>
                                                <Button colorScheme='red' onClick={onCloseDialog} ml={3}>
                                                    Confirm
                                                </Button>
                                            </AlertDialogFooter>
                                        </AlertDialogContent>
                                    </AlertDialogOverlay>
                                </AlertDialog>

                                <Modal
                                    closeOnEsc={false}
                                    closeOnOverlayClick={false}
                                    blockScrollOnMount={true} isOpen={isOpen} onClose={onClose}>
                                    <ModalOverlay />
                                    <ModalContent>
                                        <ModalBody>
                                            <Text fontWeight='bold' mb='1rem'>
                                                Please wait..
                                            </Text>
                                            <Spinner
                                                thickness='4px'
                                                speed='0.65s'
                                                emptyColor='gray.200'
                                                color='blue.500'
                                                size='xl'
                                            />
                                        </ModalBody>
                                    </ModalContent>
                                </Modal>

                                {passages && passages.map(block => (
                                    <Box p="4"
                                        borderColor="#ffc9c9"
                                        borderWidth="2px"
                                        borderRadius="lg"
                                        align="start"
                                        backgroundColor="white"
                                    >
                            
                                        <Text alignItems="start">{block.split("\n").map((i, key) => {
                                            return <div key={key}>{i}</div>;
                                        })}</Text>
                                    </Box>
                                ))}
                            </VStack>



                        </TabPanel>
                        <TabPanel>

                            <ParseResume addResume={addResume} />
                            <Resume resume={resume} deleteResume={deleteResume} />
                        </TabPanel>
                    </TabPanels>
                </Tabs>


            </Stack>
        </div>
    );
}

export default Parser;
