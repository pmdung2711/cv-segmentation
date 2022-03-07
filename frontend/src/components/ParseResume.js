import {
    Modal,
    ModalOverlay,
    ModalContent,
    ModalHeader,
    ModalFooter,
    ModalBody,
    Spinner,
    ModalCloseButton, Button, HStack, Text, useDisclosure, VStack, AlertDialog,
    AlertDialogBody,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogContent,
    AlertDialogOverlay,
    Spacer, Badge,
    IconButton
} from '@chakra-ui/react';

import { useState } from 'react';
import React, { useRef } from 'react';
import { nanoid } from 'nanoid'
import axios, { post } from 'axios'
import './drag.css'
import { FaTrash, FaFileUpload } from 'react-icons/fa';

function ParseResume({ addResume }) {

    const fileInputRef = useRef()

    const onCloseDialog = () => setIsOpenDialog(false)
    const cancelRef = useRef()

    const [isOpenDialog, setIsOpenDialog] = React.useState(false)
    const [file, setFile] = useState(false)
    const { isOpen, onOpen, onClose } = useDisclosure()
    const [fileName, setFilename] = useState(false)

    function handleChange(e) {
        e.preventDefault()
        setFilename(e.target.files[0].name)
        setFile(e.target.files[0])
    }

    function deleteFile() {
        setFilename("")
        setFile(false)
    }

    function handleSubmit(e) {

        e.preventDefault()

        console.log(file)

        if (file === false) {
            setIsOpenDialog(true)
        } else {
            const bodyFormData = new FormData();
            const url = "http://127.0.0.1:8899/upload/"
            onOpen()
            bodyFormData.append("file", file)
            axios({
                method: "post",
                url: url,
                data: bodyFormData,
                headers: { "Content-Type": "multipart/form-data" },
            }).then(response => {
                addResume(response.data)
                onClose()
            }).catch(error => {
                onClose()
            })
        }

    };

    return (
        <div>
            <form>
                <VStack mt="8">

                    <div className="drag-area">

                        <div class="icon"><i class="fas fa-cloud-upload-alt"></i></div>
                        <input multiple={false} id="file" type="file" onChange={(e) => handleChange(e)} hidden />
                        <Text borderRadius="lg" mb="4">
                            Please select a File to parse
                        </Text>
                        <label for="file">
                            <a>
                                <FaFileUpload color="grey" size={100} />
                            </a>
                        </label>
                        <HStack mt="2" mb="2">
                            <Text>{fileName}</Text>
                            <Spacer />
                            {fileName && <IconButton icon={<FaTrash />}
                            isRound='true'
                            onClick={() => deleteFile()} />}
                        </HStack>
                    </div>

                    <AlertDialog
                        isOpen={isOpenDialog}
                        leastDestructiveRef={cancelRef}
                        onClose={onCloseDialog}
                        colorScheme='red'
                    >
                        <AlertDialogOverlay>
                            <AlertDialogContent>
                                <AlertDialogHeader fontSize='lg' fontWeight='bold'>
                                    Please Select a file first
                                </AlertDialogHeader>
                                <AlertDialogFooter>
                                    <Button onClick={onCloseDialog} ml={3}>
                                        Confirm
                                    </Button>
                                </AlertDialogFooter>
                            </AlertDialogContent>
                        </AlertDialogOverlay>
                    </AlertDialog>

                    <HStack p="8" >
                        <Button colorScheme="red" px="8" type="submit" onClick={(e) => handleSubmit(e)}>Parse Resume</Button>
                        
                    </HStack>
                </VStack>


            </form>
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


        </div>
    )
}

export default ParseResume;