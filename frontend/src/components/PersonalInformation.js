
import {
    Box,
    chakra,
    Container,
    Stack,
    Text,
    Image,
    Flex,
    VStack,
    Button,
    Heading,
    SimpleGrid,
    StackDivider,
    useColorModeValue,
    VisuallyHidden,
    List,
    ListItem,
    Badge,
    TabList,
    Tabs,
    Tab,
    TabPanels,
    TabPanel,
} from '@chakra-ui/react';
import React from 'react';
import { FaInstagram, FaTwitter, FaYoutube } from 'react-icons/fa';
import { MdLocalShipping } from 'react-icons/md';




function PersonalInformation({ resume }) {

    const info = resume.data.resume_information
    const p_info = info.personal_information
    const edu_info = info.education
    const project_info = info.projects
    const summary_info = info.summary
    const work_info = info.work_experience
    const program_skill = info.program_skill
    const lang_skill = info.lang_skill
    const soft_skill = info.soft_skill
    const passage_block = resume.data.passage_block

    const color_theme = useColorModeValue('yellow.500', 'yellow.300')
    console.log("lange", lang_skill)
    return (
        <Container w="100%" maxW={'9xl'} >
            <SimpleGrid 
                columns={{ base: 1, lg: 1 }}
                py={{ base: 18, md: 3 }} w="100%" > 
                <Stack w="100%" >
                    <Box as={'header'}>
                        <Heading
                            lineHeight={1.1}
                            fontWeight={600}
                            fontSize={{ base: '2xl', sm: '4xl', lg: '5xl' }}>
                            {p_info.name}
                        </Heading>
                        <Text
                            color={useColorModeValue('gray.900', 'gray.400')}
                            fontWeight={300}
                            fontSize={'2xl'}>
                            {p_info.recent_job_title}
                        </Text>
                    </Box>

                    <Stack
                        spacing={{ base: 4, sm: 6 }}
                        direction={'column'}
                        divider={
                            <StackDivider
                                borderColor={useColorModeValue('gray.200', 'gray.600')}
                            />
                        }>
                        <VStack spacing={{ base: 4, sm: 6 }}>
                            <Text fontSize={'lg'}>
                                {
                                    summary_info.map(summary => {
                                        <Text>summary</Text>
                                    })
                                }
                            </Text>
                        </VStack>

                        <Box>
                            <Text
                                fontSize={{ base: '16px', lg: '18px' }}
                                color={useColorModeValue('yellow.500', 'yellow.300')}
                                fontWeight={'500'}
                                textTransform={'uppercase'}
                                mb={'4'}>
                                Personal Information
                            </Text>

                            <List spacing={2}>
                                <ListItem>
                                    <Text as={'span'} fontWeight={'bold'}>
                                        Name:
                                    </Text>{' '}
                                    {p_info.name}
                                </ListItem>
                                <ListItem>
                                    <Text as={'span'} fontWeight={'bold'}>
                                        Email:
                                    </Text>{' '}
                                    {p_info.email}
                                </ListItem>
                                <ListItem>
                                    <Text as={'span'} fontWeight={'bold'}>
                                        Phone Number:
                                    </Text>{' '}
                                    {p_info.phone_number}
                                </ListItem>
                                <ListItem>
                                    <Text as={'span'} fontWeight={'bold'}>
                                        Date of birth:
                                    </Text>{' '}
                                    {p_info.dob}
                                </ListItem>

                            </List>
                        </Box>

                        <Box>

                            {program_skill.length !== 0 && <div>
                                <Text
                                    fontSize={{ base: '16px', lg: '18px' }}
                                    color={color_theme}
                                    fontWeight={'500'}
                                    textTransform={'uppercase'}
                                    mb={'4'}>
                                    Programming Skills
                                </Text>
                                {program_skill.map(skill => (
                                    <Badge p="1" m="1">
                                        {skill}
                                    </Badge>
                                ))}</div>}

                            {lang_skill.length !== 0 && <div>
                                <br />
                                <Text
                                    fontSize={{ base: '16px', lg: '18px' }}
                                    color={color_theme}
                                    fontWeight={'500'}
                                    textTransform={'uppercase'}
                                    mb={'4'}>
                                    Language Skills
                                </Text>
                                {lang_skill.map(skill => (
                                    <Badge p="1" m="1">
                                        {skill}
                                    </Badge>
                                ))}</div>}

                            {soft_skill.length !== 0 && <div>
                                <br />
                                <Text
                                    fontSize={{ base: '16px', lg: '18px' }}
                                    color={color_theme}
                                    fontWeight={'500'}
                                    textTransform={'uppercase'}
                                    mb={'4'}>
                                    Soft Skills
                                </Text>
                                {soft_skill.map(skill => (
                                    <Badge p="1" m="1">
                                        {skill}
                                    </Badge>
                                ))}</div>}


                        </Box>
                        {edu_info.length !== 0 && (
                            <Box>
                                <Text
                                    fontSize={{ base: '16px', lg: '18px' }}
                                    color={color_theme}
                                    fontWeight={'500'}
                                    textTransform={'uppercase'}
                                    mb={'4'}>
                                    Education
                                </Text>

                                <Tabs>
                                    <TabList>
                                        {edu_info.map(edu => (
                                            <Tab>
                                                Education {edu.id + 1}
                                            </Tab>
                                        ))}
                                    </TabList>
                                    <TabPanels>

                                        {edu_info.map(edu => (
                                            <TabPanel>
                                                <Box
                                                    borderColor="grey.100"
                                                    borderWidth="2px"
                                                    p="2"
                                                    borderRadius="lg"
                                                    m="1"
                                                    key={edu.id}>
                                                    <List spacing={2}>
                                                        <ListItem>
                                                            <Text as={'span'} fontWeight={'bold'}>
                                                                From:
                                                            </Text>{' '}
                                                            {edu.edu_duration.du_from}
                                                        </ListItem>
                                                        <ListItem>
                                                            <Text as={'span'} fontWeight={'bold'}>
                                                                To:
                                                            </Text>{' '}
                                                            {edu.edu_duration.du_to}
                                                        </ListItem>
                                                        <ListItem>
                                                            <Text as={'span'} fontWeight={'bold'}>
                                                                Education Level:
                                                            </Text>{' '}
                                                            {edu.education_level}
                                                        </ListItem>
                                                        <ListItem>
                                                            <Text as={'span'} fontWeight={'bold'}>
                                                                GPA:
                                                            </Text>{' '}
                                                            {edu.gpa}
                                                        </ListItem>
                                                        <ListItem>
                                                            <Text as={'span'} fontWeight={'bold'}>
                                                                Passage ID  :
                                                            </Text>{' '}
                                                            {edu.passage_id}
                                                        </ListItem>

                                                    </List>
                                                </Box>
                                                <Box
                                                    borderColor="grey.100"
                                                    borderWidth="2px"
                                                    p="2"
                                                    borderRadius="lg"
                                                    m="1">
                                                    <Text>
                                                        {passage_block[edu.passage_id].content.split("\n").map((i, key) => {
                                                                return <div key={key}>{i}</div>;
                                                                })}
                                                    </Text>
                                                </Box>
                                            </TabPanel>
                                        ))}


                                    </TabPanels>
                                </Tabs>



                            </Box>
                        )}

                        {work_info.length !== 0 && (
                            <Box>
                                <Text
                                    fontSize={{ base: '16px', lg: '18px' }}
                                    color={color_theme}
                                    fontWeight={'500'}
                                    textTransform={'uppercase'}
                                    mb={'4'}>
                                    Work Experience
                                </Text>

                                <Tabs size='md' variant='enclosed'>
                                    <TabList>
                                        {work_info.map(work => (
                                            <Tab>
                                                Work Experience {work.id + 1}
                                            </Tab>
                                        ))}
                                    </TabList>
                                    <TabPanels>
                                        {work_info.map(work => (
                                            <TabPanel>
                                                <Box
                                                    borderColor="grey.100"
                                                    borderWidth="2px"
                                                    p="2"
                                                    borderRadius="lg"
                                                    m="1"
                                                    key={work.id}>

                                                    <List spacing={2}>

                                                        <ListItem>
                                                            <Text as={'span'} fontWeight={'bold'}>
                                                                Job Title:
                                                            </Text>{' '}
                                                            {work.job_title[0]}
                                                        </ListItem>
                                                        <ListItem>
                                                            <Text as={'span'} fontWeight={'bold'}>
                                                                Relevant Job Title:
                                                            </Text>{' '}
                                                            {work.relevant_job_title[0]}
                                                        </ListItem>
                                                        <ListItem>
                                                            <Text as={'span'} fontWeight={'bold'}>
                                                                From:
                                                            </Text>{' '}
                                                            {work.work_duration.du_from}
                                                        </ListItem>
                                                        <ListItem>
                                                            <Text as={'span'} fontWeight={'bold'}>
                                                                To:
                                                            </Text>{' '}
                                                            {work.work_duration.du_to}
                                                        </ListItem>

                                                        <ListItem>
                                                            <Text as={'span'} fontWeight={'bold'}>
                                                                Months:
                                                            </Text>{' '}
                                                            {work.work_duration.months}
                                                        </ListItem>
                                                        <ListItem>
                                                            <Text as={'span'} fontWeight={'bold'}>
                                                                Years:
                                                            </Text>{' '}
                                                            {work.work_duration.years}
                                                        </ListItem>
                                                        <ListItem>
                                                            <Text as={'span'} fontWeight={'bold'}>
                                                                Passage ID  :
                                                            </Text>{' '}
                                                            {work.passage_id}
                                                        </ListItem>

                                                    </List>
                                                </Box>
                                                <Box
                                                    borderColor="grey.100"
                                                    borderWidth="2px"
                                                    p="2"
                                                    borderRadius="lg"
                                                    m="1">
                                                    <Text>
                                                        {passage_block[work.passage_id].content.split("\n").map((i, key) => {
                                                                return <div key={key}>{i}</div>;
                                                                })}
                                                    </Text>
                                                </Box>
                                            </TabPanel>

                                        ))}
                                    </TabPanels>
                                </Tabs>



                            </Box>
                        )}

                        {project_info.length !== 0 && (
                            <Box>
                                <Text
                                    fontSize={{ base: '16px', lg: '18px' }}
                                    color={color_theme}
                                    fontWeight={'500'}
                                    textTransform={'uppercase'}
                                    mb={'4'}>
                                    Projects
                                </Text>

                                <Tabs size='md' variant='enclosed'>
                                    <TabList>
                                        {project_info.map(project => (
                                            <Tab>
                                                Project {project.id + 1}
                                            </Tab>
                                        ))}
                                    </TabList>
                                    <TabPanels>
                                        {project_info.map(project => (
                                            <TabPanel>
                                                <Box
                                                    borderColor="grey.100"
                                                    borderWidth="2px"
                                                    p="2"
                                                    borderRadius="lg"
                                                    m="1"
                                                    key={project.id}>

                                                    <List spacing={2}>

                                                        <ListItem>
                                                            <Text as={'span'} fontWeight={'bold'}>
                                                                Position:
                                                            </Text>{' '}
                                                            {project.job_title[0]}
                                                        </ListItem>
                                                        <ListItem>
                                                            <Text as={'span'} fontWeight={'bold'}>
                                                                Relevant Position:
                                                            </Text>{' '}
                                                            {project.relevant_job_title[0]}
                                                        </ListItem>
                                                        <ListItem>
                                                            <Text as={'span'} fontWeight={'bold'}>
                                                                From:
                                                            </Text>{' '}
                                                            {project.work_duration.du_from}
                                                        </ListItem>
                                                        <ListItem>
                                                            <Text as={'span'} fontWeight={'bold'}>
                                                                To:
                                                            </Text>{' '}
                                                            {project.work_duration.du_to}
                                                        </ListItem>

                                                        <ListItem>
                                                            <Text as={'span'} fontWeight={'bold'}>
                                                                Months:
                                                            </Text>{' '}
                                                            {project.work_duration.months}
                                                        </ListItem>
                                                        <ListItem>
                                                            <Text as={'span'} fontWeight={'bold'}>
                                                                Years:
                                                            </Text>{' '}
                                                            {project.work_duration.years}
                                                        </ListItem>
                                                        <ListItem>
                                                            <Text as={'span'} fontWeight={'bold'}>
                                                                Passage ID  :
                                                            </Text>{' '}
                                                            {project.passage_id}
                                                        </ListItem>

                                                    </List>
                                                </Box>
                                                <Box
                                                    borderColor="grey.100"
                                                    borderWidth="2px"
                                                    p="2"
                                                    borderRadius="lg"
                                                    m="1">
                                                    <Text>
                                                        {passage_block[project.passage_id].content.split("\n").map((i, key) => {
                                                                return <div key={key}>{i}</div>;
                                                                })}
                                                    </Text>
                                                </Box>
                                            </TabPanel>

                                        ))}
                                    </TabPanels>
                                </Tabs>



                            </Box>
                        )}



                    </Stack>



                    <Stack direction="row" alignItems="center" justifyContent={'center'}>
                        <Text>Date: {resume.date}</Text>
                    </Stack>
                </Stack>
            </SimpleGrid>
        </Container>
    )

};


export default PersonalInformation;