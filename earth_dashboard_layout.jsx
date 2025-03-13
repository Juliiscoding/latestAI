/**
 * Earth Module Dashboard Layout
 * 
 * This component serves as the main layout for the Earth module dashboard.
 * It provides the structure and navigation for all Earth module pages.
 */

import React, { useState } from 'react';
import { useRouter } from 'next/router';
import {
  Box,
  Flex,
  Text,
  Icon,
  HStack,
  VStack,
  useColorModeValue,
  Drawer,
  DrawerContent,
  IconButton,
  useDisclosure,
  CloseButton,
  Heading,
  Avatar,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
} from '@chakra-ui/react';
import {
  FiHome,
  FiTrendingUp,
  FiCompass,
  FiStar,
  FiSettings,
  FiMenu,
  FiBell,
  FiChevronDown,
  FiUsers,
  FiPackage,
  FiShoppingCart,
  FiBarChart2,
  FiDatabase,
} from 'react-icons/fi';

// Navigation items for the sidebar
const LinkItems = [
  { name: 'Overview', icon: FiHome, href: '/earth' },
  { name: 'Sales Analytics', icon: FiTrendingUp, href: '/earth/sales' },
  { name: 'Customers', icon: FiUsers, href: '/earth/customers' },
  { name: 'Products', icon: FiPackage, href: '/earth/products' },
  { name: 'Inventory', icon: FiDatabase, href: '/earth/inventory' },
  { name: 'Shops', icon: FiShoppingCart, href: '/earth/shops' },
  { name: 'Recommendations', icon: FiStar, href: '/earth/recommendations' },
  { name: 'Reports', icon: FiBarChart2, href: '/earth/reports' },
  { name: 'Settings', icon: FiSettings, href: '/earth/settings' },
];

export default function EarthDashboardLayout({ children }) {
  const { isOpen, onOpen, onClose } = useDisclosure();
  
  return (
    <Box minH="100vh" bg={useColorModeValue('gray.50', 'gray.900')}>
      <SidebarContent
        onClose={() => onClose}
        display={{ base: 'none', md: 'block' }}
      />
      <Drawer
        isOpen={isOpen}
        placement="left"
        onClose={onClose}
        returnFocusOnClose={false}
        onOverlayClick={onClose}
        size="full">
        <DrawerContent>
          <SidebarContent onClose={onClose} />
        </DrawerContent>
      </Drawer>
      {/* Mobile nav */}
      <MobileNav onOpen={onOpen} />
      <Box ml={{ base: 0, md: 60 }} p="4">
        {children}
      </Box>
    </Box>
  );
}

// Sidebar component
const SidebarContent = ({ onClose, ...rest }) => {
  const router = useRouter();
  
  return (
    <Box
      transition="3s ease"
      bg={useColorModeValue('white', 'gray.900')}
      borderRight="1px"
      borderRightColor={useColorModeValue('gray.200', 'gray.700')}
      w={{ base: 'full', md: 60 }}
      pos="fixed"
      h="full"
      {...rest}>
      <Flex h="20" alignItems="center" mx="8" justifyContent="space-between">
        <Flex alignItems="center">
          <Icon as={FiCompass} h={8} w={8} color="blue.500" />
          <Text fontSize="2xl" fontWeight="bold" ml="2">
            Earth
          </Text>
        </Flex>
        <CloseButton display={{ base: 'flex', md: 'none' }} onClick={onClose} />
      </Flex>
      {LinkItems.map((link) => (
        <NavItem 
          key={link.name} 
          icon={link.icon} 
          href={link.href}
          isActive={router.pathname === link.href || router.pathname.startsWith(`${link.href}/`)}
        >
          {link.name}
        </NavItem>
      ))}
    </Box>
  );
};

// Navigation item component
const NavItem = ({ icon, children, href, isActive, ...rest }) => {
  const router = useRouter();
  const activeColor = useColorModeValue('blue.500', 'blue.200');
  const activeBackground = useColorModeValue('blue.50', 'blue.900');
  
  return (
    <Box
      as="a"
      href={href}
      style={{ textDecoration: 'none' }}
      onClick={(e) => {
        e.preventDefault();
        router.push(href);
      }}
      _focus={{ boxShadow: 'none' }}>
      <Flex
        align="center"
        p="4"
        mx="4"
        borderRadius="lg"
        role="group"
        cursor="pointer"
        color={isActive ? activeColor : useColorModeValue('gray.600', 'gray.200')}
        bg={isActive ? activeBackground : 'transparent'}
        fontWeight={isActive ? 'bold' : 'normal'}
        _hover={{
          bg: useColorModeValue('blue.50', 'blue.900'),
          color: useColorModeValue('blue.500', 'blue.200'),
        }}
        {...rest}>
        {icon && (
          <Icon
            mr="4"
            fontSize="16"
            as={icon}
          />
        )}
        {children}
      </Flex>
    </Box>
  );
};

// Mobile navigation component
const MobileNav = ({ onOpen, ...rest }) => {
  const router = useRouter();
  
  // Extract breadcrumb items from the current path
  const pathSegments = router.pathname.split('/').filter(Boolean);
  const breadcrumbs = pathSegments.map((segment, index) => {
    const href = `/${pathSegments.slice(0, index + 1).join('/')}`;
    return {
      name: segment.charAt(0).toUpperCase() + segment.slice(1),
      href,
    };
  });
  
  return (
    <Flex
      ml={{ base: 0, md: 60 }}
      px={{ base: 4, md: 4 }}
      height="20"
      alignItems="center"
      bg={useColorModeValue('white', 'gray.900')}
      borderBottomWidth="1px"
      borderBottomColor={useColorModeValue('gray.200', 'gray.700')}
      justifyContent={{ base: 'space-between', md: 'flex-end' }}
      {...rest}>
      <IconButton
        display={{ base: 'flex', md: 'none' }}
        onClick={onOpen}
        variant="outline"
        aria-label="open menu"
        icon={<FiMenu />}
      />
      
      <Flex display={{ base: 'flex', md: 'none' }} alignItems="center">
        <Icon as={FiCompass} h={8} w={8} color="blue.500" />
        <Text fontSize="2xl" fontWeight="bold" ml="2">
          Earth
        </Text>
      </Flex>
      
      <Breadcrumb display={{ base: 'none', md: 'flex' }} spacing="8px" separator="/">
        <BreadcrumbItem>
          <BreadcrumbLink href="/">Home</BreadcrumbLink>
        </BreadcrumbItem>
        
        {breadcrumbs.map((breadcrumb, index) => (
          <BreadcrumbItem key={index} isCurrentPage={index === breadcrumbs.length - 1}>
            <BreadcrumbLink href={breadcrumb.href}>
              {breadcrumb.name}
            </BreadcrumbLink>
          </BreadcrumbItem>
        ))}
      </Breadcrumb>

      <HStack spacing={{ base: '0', md: '6' }}>
        <IconButton
          size="lg"
          variant="ghost"
          aria-label="open menu"
          icon={<FiBell />}
        />
        <Flex alignItems={'center'}>
          <Menu>
            <MenuButton
              py={2}
              transition="all 0.3s"
              _focus={{ boxShadow: 'none' }}>
              <HStack>
                <Avatar
                  size={'sm'}
                  name="User"
                />
                <VStack
                  display={{ base: 'none', md: 'flex' }}
                  alignItems="flex-start"
                  spacing="1px"
                  ml="2">
                  <Text fontSize="sm">Admin User</Text>
                  <Text fontSize="xs" color="gray.600">
                    Administrator
                  </Text>
                </VStack>
                <Box display={{ base: 'none', md: 'flex' }}>
                  <FiChevronDown />
                </Box>
              </HStack>
            </MenuButton>
            <MenuList
              bg={useColorModeValue('white', 'gray.900')}
              borderColor={useColorModeValue('gray.200', 'gray.700')}>
              <MenuItem>Profile</MenuItem>
              <MenuItem>Settings</MenuItem>
              <MenuDivider />
              <MenuItem>Sign out</MenuItem>
            </MenuList>
          </Menu>
        </Flex>
      </HStack>
    </Flex>
  );
};
