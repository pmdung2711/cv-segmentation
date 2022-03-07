import {
  Heading,
  VStack,
  useColorMode, Tabs, TabList, TabPanels, Tab, TabPanel, Input, Textarea
  , Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  Spinner,
  ModalCloseButton, Button, HStack, Text, useDisclosure, AlertDialog, Box, Badge,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay,
  Spacer,
  IconButton,
  Flex
} from '@chakra-ui/react';
import { FaSun, FaMoon, FaFacebook, FaGithub, FaLinkedinIn } from 'react-icons/fa'
import ParseResume from './components/ParseResume';
import { useState, useEffect } from 'react'
import Resume from './components/Resume';
import React, { useRef } from 'react';
import { nanoid } from 'nanoid'
import axios, { post } from 'axios'
import Header from './components/Header'
import Hero from './components/Hero'
import Features from './components/Features'
import Footer from './components/Footer'
import Parser from './components/Parser'
function App() {

 

  return (
    <div>
      <Header></Header>
      <Hero></Hero>
      <Parser />
      <Footer />
    </div>
  );
}

export default App;
